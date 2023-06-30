from typing import List, Optional, Dict

from fastapi.logger import logger
from mysqlsb import MySQLStatementBuilder, FetchType
from mysql.connector.pooling import PooledMySQLConnection

from sedbackend.apps.core.exceptions import NoChangeException
from sedbackend.apps.core.applications.state import get_application
import sedbackend.apps.core.projects.models as models
import sedbackend.apps.core.projects.exceptions as exc
from sedbackend.apps.core.users.storage import db_get_users_with_ids

PROJECTS_TABLE = 'projects'
PROJECTS_COLUMNS = ['id', 'name']
SUBPROJECTS_TABLE = 'projects_subprojects'
SUBPROJECT_COLUMNS = ['id', 'name', 'application_sid', 'project_id', 'native_project_id', 'owner_id',
                      'datetime_created']
PROJECTS_PARTICIPANTS_TABLE = 'projects_participants'
PROJECTS_PARTICIPANTS_COLUMNS = ['id', 'user_id', 'project_id', 'access_level']


def db_get_projects(connection, user_id: int, segment_length: int = 0, index: int = 0) -> List[models.ProjectListing]:

    if index < 0:
        index = 0

    if segment_length < 0:
        segment_length = 0

    with connection.cursor(prepared=True) as cursor:
        select_stmnt = 'SELECT projects.name, projects.id as pid, ' \
                       'projects.datetime_created, ' \
                       '(SELECT count(*) as participant_count FROM projects_participants WHERE project_id = pid), ' \
                       '(SELECT access_level FROM projects_participants WHERE project_id = pid AND user_id = %s) ' \
                       'FROM projects ' \
                       f'ORDER BY `projects`.`datetime_created` ASC ' \
                       f'LIMIT {segment_length} OFFSET {segment_length * index} '

        values = [user_id]
        logger.debug(f'db_get_projects: {select_stmnt} with values {values}')
        cursor.execute(select_stmnt, values)
        rs = cursor.fetchall()

        project_list = []
        for res in rs:
            res_dict = dict(zip(['name', 'pid', 'datetime_created', 'participant_count', 'access_level'], res))

            access_level = res_dict["access_level"]
            if access_level is None:
                access_level = 0

            pl = models.ProjectListing(id=res_dict['pid'], name=res_dict['name'],
                                       access_level=models.AccessLevel(access_level),
                                       participants=res_dict["participant_count"],
                                       datetime_created=res_dict['datetime_created'])
            project_list.append(pl)

    return project_list


def db_get_user_projects(connection, user_id: int, segment_length: int = 0, index: int = 0) \
        -> List[models.ProjectListing]:

    if index < 0:
        index = 0

    if segment_length < 0:
        segment_length = 0

    with connection.cursor(prepared=True) as cursor:
        select_stmnt = 'SELECT projects_participants.access_level, projects.name, projects.id as pid, ' \
                       'projects.datetime_created, ' \
                       '(SELECT count(*) as participant_count FROM projects_participants WHERE project_id = pid) ' \
                       'FROM projects ' \
                       'INNER JOIN projects_participants ON projects_participants.project_id = projects.id ' \
                       f'WHERE projects_participants.user_id = %s ' \
                       f'ORDER BY `projects`.`datetime_created` ASC '
        if segment_length != 0:
            select_stmnt += f'LIMIT {segment_length} OFFSET {segment_length * index} ' \


        values = [user_id]
        logger.debug(f'db_get_user_projects: {select_stmnt} with values {values}')
        cursor.execute(select_stmnt, values)
        rs = cursor.fetchall()

        project_list = []
        for res in rs:
            res_dict = dict(zip(['access_level', 'name', 'pid', 'datetime_created', 'participant_count'], res))
            pl = models.ProjectListing(id=res_dict['pid'], name=res_dict['name'],
                                       access_level=models.AccessLevel(res_dict["access_level"]),
                                       participants=res_dict["participant_count"],
                                       datetime_created=res_dict['datetime_created'])
            project_list.append(pl)

    return project_list


def db_get_participant_count (connection, project_id) -> int:
    select_stmnt = MySQLStatementBuilder(connection)
    res = select_stmnt\
        .count(PROJECTS_PARTICIPANTS_TABLE)\
        .where('project_id = %s', [project_id])\
        .execute(dictionary=True)

    return res["count"]


def db_get_project(connection, project_id) -> models.Project:
    proj_sql = MySQLStatementBuilder(connection)
    proj_db_res = proj_sql \
        .select(PROJECTS_TABLE, PROJECTS_COLUMNS) \
        .where('id = %s', [project_id]) \
        .execute(fetch_type=FetchType.FETCH_ONE, dictionary=True)

    if proj_db_res is None:
        raise exc.ProjectNotFoundException

    project = models.Project(id=proj_db_res['id'], name=proj_db_res['name'])

    part_sql = MySQLStatementBuilder(connection)
    participant_rows = part_sql \
        .select(PROJECTS_PARTICIPANTS_TABLE, PROJECTS_PARTICIPANTS_COLUMNS) \
        .where('project_id = %s', [project_id]) \
        .execute(fetch_type=FetchType.FETCH_ALL, dictionary=True)

    participant_ids = []
    for participant_db in participant_rows:
        participant_ids.append(participant_db['user_id'])
        project.participants_access[participant_db['user_id']] = participant_db['access_level']

    if len(participant_ids) == 0:
        logger.error(f"This project (id = {project_id}) does not have any participants")
        raise exc.NoParticipantsException()

    project.participants = db_get_users_with_ids(connection, participant_ids)

    project.subprojects = db_get_subprojects(connection, project_id)

    return project


def db_post_project(connection, project: models.ProjectPost, owner_id: int) -> models.Project:
    # Set owner if it is not already set
    if owner_id not in project.participants:
        project.participants.append(owner_id)

    project.participants_access[owner_id] = models.AccessLevel.OWNER

    project_sql = MySQLStatementBuilder(connection)
    project_cols = ['name']
    project_sql.insert(PROJECTS_TABLE, project_cols).set_values([project.name]).execute(return_affected_rows=True)
    project_id = project_sql.last_insert_id

    for participant_id in project.participants:
        access_level = project.participants_access.get(participant_id)

        if access_level is None:
            raise exc.ParticipantInconsistencyException('Participant is listed, but was not assigned an access level.')

        db_add_participant(connection, project_id, participant_id, access_level, check_project_exists=False)

    if len(project.subprojects) > 0:
        db_update_subprojects_project_association(connection, project.subprojects, project_id)

    return db_get_project(connection, project_id)


def db_clear_subproject_project_association(connection: PooledMySQLConnection, subproject_id_list: List[int], current_project_id: int):
    logger.debug(f"Clearing subproject association with project with ID = {current_project_id} "
                 f"for subprojects with IDs {str(subproject_id_list)})")

    update_stmnt = MySQLStatementBuilder(connection)
    update_stmnt.update(SUBPROJECTS_TABLE, "project_id = NULL", [])\
        .where(f'id IN {MySQLStatementBuilder.placeholder_array(len(subproject_id_list))}', subproject_id_list)\
        .execute()


def db_update_participants(connection: PooledMySQLConnection,
                           project_id: int,
                           participants_access_map: Dict[int, models.AccessLevel]):
    logger.debug(f'Updating participants for project with ID {project_id} to {participants_access_map}')

    # This could be turned into a single db-call using CASE-WHEN-THEN, but it would be too complex for the gains
    for participant_id, access_level in participants_access_map.items():
        update_stmnt = MySQLStatementBuilder(connection)
        update_stmnt.update(PROJECTS_PARTICIPANTS_TABLE, 'access_level = %s', [access_level.value])\
            .where('project_id = %s AND user_id = %s', [project_id, participant_id])\
            .execute()

    return


def db_update_subprojects_project_association(connection: PooledMySQLConnection, subproject_id_list: List[int],
                                              project_id: int, overwrite: bool = False):
    logger.debug(f'Associating sub-projects with IDs {subproject_id_list} to project with ID {project_id}')

    if overwrite is False:
        # Assert that these subprojects are not already members of other projects
        select_stmnt = MySQLStatementBuilder(connection)
        rs = select_stmnt.select(SUBPROJECTS_TABLE, ['project_id', 'id', 'name'])\
            .where(f'id IN {MySQLStatementBuilder.placeholder_array(len(subproject_id_list))}', subproject_id_list)\
            .execute(fetch_type=FetchType.FETCH_ALL, dictionary=True)

        for res in rs:
            if res['project_id'] is not None:
                raise exc.ConflictingProjectAssociationException(f'Subproject "{res["name"]}" (id: {res["id"]}) '
                                                                 f'is already associated with another project, '
                                                                 f'and overwrite has been disabled.')

    update_stmnt = MySQLStatementBuilder(connection)
    update_stmnt\
        .update(SUBPROJECTS_TABLE, "project_id = %s", [project_id])\
        .where(f'id IN {MySQLStatementBuilder.placeholder_array(len(subproject_id_list))}', subproject_id_list)\
        .execute(fetch_type=FetchType.FETCH_NONE)

    return


def db_delete_project(connection, project_id: int) -> bool:
    logger.debug(f"Removing project: {project_id}")

    db_get_project_exists(connection, project_id) # If the project does not exist, this raises the appropriate exception

    del_sql = MySQLStatementBuilder(connection)
    res, row_count = del_sql.delete(PROJECTS_TABLE).where('id = %s', [project_id]).execute(return_affected_rows=True)
    if row_count == 0:
        raise exc.ProjectNotDeletedException("Unable to remove project")

    return True


def db_add_participant(connection, project_id, user_id, access_level, check_project_exists=True) -> bool:
    if check_project_exists:
        db_get_project_exists(connection, project_id)  # Raises exception if project does not exist

    participants_sql = MySQLStatementBuilder(connection)
    participants_cols = ['user_id', 'project_id', 'access_level']
    participants_sql.insert(PROJECTS_PARTICIPANTS_TABLE, participants_cols)\
        .set_values([user_id, project_id, access_level])\
        .execute()

    return True


def db_add_participants(connection: PooledMySQLConnection, project_id: int,
                        user_id_access_map: Dict[int, models.AccessLevel], check_project_exists=True) -> bool:
    if check_project_exists:
        db_get_project_exists(connection, project_id)   # Raises exception if project does not exist

    insert_stmnt = MySQLStatementBuilder(connection)
    insert_stmnt.insert(PROJECTS_PARTICIPANTS_TABLE, ['user_id', 'project_id', 'access_level'])

    insert_values = []
    for user_id, access_level in user_id_access_map.items():
        insert_values.append([user_id, project_id, access_level])

    insert_stmnt.set_values(insert_values).execute()

    return True


def db_delete_participant(connection, project_id, user_id, check_project_exists=True) -> bool:
    if check_project_exists:
        db_get_project_exists(connection, project_id)  # Raises exception if project does not exist

    participants_sql = MySQLStatementBuilder(connection)
    res, row_count = participants_sql\
        .delete(PROJECTS_PARTICIPANTS_TABLE)\
        .where('project_id = %s AND user_id = %s', [project_id, user_id])\
        .execute(return_affected_rows=True)

    if row_count == 0:
        raise exc.ParticipantChangeException("Failed to remove participant from project")

    return True


def db_delete_participants(connection: PooledMySQLConnection, project_id: int, user_ids: List[int],
                           check_project_exists=True) -> bool:

    logger.debug(f"Removing participants with ids = {user_ids} from project with id = {project_id}")

    if check_project_exists:
        db_get_project_exists(connection, project_id)

    del_stmnt = MySQLStatementBuilder(connection)
    values = [project_id]
    values.extend(user_ids)
    res, row_count = del_stmnt\
        .delete(PROJECTS_PARTICIPANTS_TABLE)\
        .where(f'project_id = %s AND user_id IN {MySQLStatementBuilder.placeholder_array(len(user_ids))}',
               values).execute(return_affected_rows=True)

    if row_count != len(user_ids):
        raise NoChangeException('Not all participants could be found')

    return True


def db_put_name(connection, project_id, name) -> bool:

    project = db_get_project(connection, project_id)    # Raises exception if project does not exist

    if project.name == name:
        return True

    project_sql = MySQLStatementBuilder(connection)
    res, row_count = project_sql\
        .update(PROJECTS_TABLE, "name = %s", [name]).where('id = %s', [project_id])\
        .execute(return_affected_rows=True)

    logger.debug(f"Affected rows: {row_count}")

    if row_count == 0:
        raise exc.ProjectChangeException("Failed to update project information")

    return True


def db_post_subproject(connection, subproject: models.SubProjectPost, current_user_id: int, project_id: Optional[int] = None) \
        -> models.SubProject:

    if project_id is not None:
        db_get_project_exists(connection, project_id)   # Raises exception if the project does not exist

    # Avoid duplicates
    try:
        duplicate = db_get_subproject_native(connection, subproject.application_sid, subproject.native_project_id)
        if duplicate is not None:
            raise exc.SubProjectDuplicateException
    except exc.SubProjectNotFoundException:
        insert_stmnt = MySQLStatementBuilder(connection)
        insert_stmnt\
            .insert(SUBPROJECTS_TABLE, ['name', 'application_sid', 'project_id', 'native_project_id', 'owner_id'])\
            .set_values([subproject.name, subproject.application_sid, project_id, subproject.native_project_id, current_user_id])\
            .execute()

        return db_get_subproject_native(connection, subproject.application_sid, subproject.native_project_id)


def db_get_subprojects(connection: PooledMySQLConnection, project_id: int) \
        -> List[models.SubProject]:
    # Assert that the project exists
    db_get_project_exists(connection, project_id)  # Throws if project does not exist

    select_stmnt = MySQLStatementBuilder(connection)
    rs = select_stmnt.select(SUBPROJECTS_TABLE, SUBPROJECT_COLUMNS)\
        .where('project_id = ?', [project_id])\
        .execute(fetch_type=FetchType.FETCH_ALL, dictionary=True)

    subproject_list = []

    if rs is None:
        return subproject_list

    for res in rs:
        subproject = models.SubProject(**res)
        subproject_list.append(subproject)

    return subproject_list


def db_get_subproject(connection, project_id, subproject_id) -> models.SubProject:
    db_get_project_exists(connection, project_id) # Raises exception if project does not exist

    select_stmnt = MySQLStatementBuilder(connection)
    res = select_stmnt\
        .select(SUBPROJECTS_TABLE, SUBPROJECT_COLUMNS)\
        .where("id = %s AND project_id = %s", [subproject_id, project_id])\
        .execute(fetch_type=FetchType.FETCH_ONE, dictionary=True)

    if res is None:
        raise exc.SubProjectNotFoundException

    sub_project = models.SubProject(**res)

    return sub_project


def db_get_subproject_with_id(connection, subproject_id) -> models.SubProject:
    select_stmnt = MySQLStatementBuilder(connection)
    res = select_stmnt\
        .select(SUBPROJECTS_TABLE, SUBPROJECT_COLUMNS)\
        .where("id = %s", [subproject_id])\
        .execute(fetch_type=FetchType.FETCH_ONE, dictionary=True)

    if res is None:
        raise exc.SubProjectNotFoundException

    sub_project = models.SubProject(**res)

    return sub_project


def db_get_subproject_native(connection, application_sid, native_project_id) -> models.SubProject:
    get_application(application_sid)        # Raises exception of application does not exist

    select_stmnt = MySQLStatementBuilder(connection)
    res = select_stmnt\
        .select(SUBPROJECTS_TABLE, SUBPROJECT_COLUMNS)\
        .where("native_project_id = %s AND application_sid = %s", [native_project_id, application_sid])\
        .execute(fetch_type=FetchType.FETCH_ONE, dictionary=True)

    if res is None:
        raise exc.SubProjectNotFoundException

    sub_project = models.SubProject(**res)

    return sub_project


def db_delete_subproject(connection, project_id, subproject_id) -> bool:
    delete_stmnt = MySQLStatementBuilder(connection)
    delete_stmnt.delete(SUBPROJECTS_TABLE)

    if project_id is not None:
        delete_stmnt.where("project_id = %s AND id = %s", [project_id, subproject_id])
    else:
        delete_stmnt.where("id = %s AND project_id IS NULL", [subproject_id])

    res, row_count = delete_stmnt.execute(return_affected_rows=True)

    if row_count == 0:
        raise exc.SubProjectNotDeletedException

    return True


def db_get_user_subprojects_with_application_sid(con, user_id, application_sid,
                                                 no_project_association: Optional[bool] = False) \
        -> List[models.SubProject]:

    logger.debug(f"Getting subprojects for user {user_id} and application {application_sid}, "
                 f"with no project association: {no_project_association}")
    # Validate that the application is listed
    get_application(application_sid)

    # Get projects in which this user is a participant
    project_list = db_get_user_projects(con, user_id)
    project_id_list = []
    for project in project_list:
        project_id_list.append(project.id)

    # Figure out which of those projects have an attached subproject with specified application SID.
    where_values = [application_sid]
    where_values.extend(project_id_list.copy())
    where_values.append(user_id)
    where_stmnt = f"application_sid = %s AND ("
    if len(project_id_list) != 0:
        where_stmnt += f"(project_id IN {MySQLStatementBuilder.placeholder_array(len(project_id_list))}) OR "
    where_stmnt += f"(project_id is null AND owner_id = %s))"

    stmnt = MySQLStatementBuilder(con)
    rs = stmnt.select(SUBPROJECTS_TABLE, SUBPROJECT_COLUMNS)\
        .where(where_stmnt,
               where_values)\
        .execute(fetch_type=FetchType.FETCH_ALL, dictionary=True)

    # Serialize & return
    subproject_list = []
    for res in rs:
        subproject_list.append(models.SubProject(**res))

    if no_project_association:
        subproject_list = list(filter(lambda p: p.project_id is None, subproject_list))

    return subproject_list


def db_update_project(con: PooledMySQLConnection, project_updated: models.ProjectEdit) -> models.Project:

    # Check if project exists
    project_original = db_get_project(con, project_updated.id)

    # Change name if requested
    if project_original.name != project_updated.name:
        update_project_stmnt = MySQLStatementBuilder(con)
        res, row_count = update_project_stmnt\
            .update(PROJECTS_TABLE, "name = %s", [project_updated.name])\
            .where("id = %s", [project_updated.id])\
            .execute(fetch_type=FetchType.FETCH_NONE, return_affected_rows=True)
        if row_count != 1:
            raise NoChangeException

    # Remove participants if requested
    if len(project_updated.participants_to_remove) > 0:
        db_delete_participants(con, project_updated.id, project_updated.participants_to_remove, check_project_exists=False)

    # Remove subprojects if requested
    if len(project_updated.subprojects_to_remove) > 0:
        db_clear_subproject_project_association(con, project_updated.subprojects_to_remove, project_updated.id)

    # Add participants if requested
    if len(project_updated.participants_to_add.keys()) > 0:
        db_add_participants(con, project_updated.id, project_updated.participants_to_add, check_project_exists=False)

    # Add subprojects if requested
    if len(project_updated.subprojects_to_add) > 0:
        db_update_subprojects_project_association(con, project_updated.subprojects_to_add, project_updated.id, overwrite=False)

    # Update participants if requested
    if len(project_updated.participants_to_update.keys()) > 0:
        db_update_participants(con, project_updated.id, project_updated.participants_to_update)

    # Return project
    return db_get_project(con, project_updated.id)


def db_get_project_exists(connection: PooledMySQLConnection, project_id: int) -> bool:
    """
    Convenience function for asserting that a project exists. Faster than getting and building the entire project.
    :param connection:
    :param project_id:
    :return:
    """
    select_stmnt = MySQLStatementBuilder(connection)
    res = select_stmnt.select(PROJECTS_TABLE, ['id'])\
        .where('id = ?', [project_id])\
        .execute(fetch_type=FetchType.FETCH_ONE)

    if res is None:
        raise exc.ProjectNotFoundException

    return True


def db_delete_subproject_native(connection: PooledMySQLConnection, application_id: str, native_project_id: int):
    delete_stmnt = MySQLStatementBuilder(connection)
    res, row_count = delete_stmnt\
        .delete(SUBPROJECTS_TABLE)\
        .where("application_sid = ? AND native_project_id = ?", [application_id, native_project_id])\
        .execute(fetch_type=FetchType.FETCH_NONE, return_affected_rows=True)

    if row_count == 0:
        raise exc.SubProjectNotFoundException

    return True

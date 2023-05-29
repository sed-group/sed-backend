from typing import List, Optional

from fastapi.logger import logger
from mysqlsb import MySQLStatementBuilder, FetchType, utils
from mysql.connector.pooling import PooledMySQLConnection

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
    logger.debug('Adding new project:')
    logger.debug(project)

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


def db_update_subprojects_project_association(connection: PooledMySQLConnection, subproject_id_list: List[int],
                                              project_id: int):
    logger.debug(f'Associating sub-projects with IDs {subproject_id_list} to project with ID {project_id}')

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
    db_get_subproject(connection, project_id, subproject_id)  # Raises exception if project does not exist

    delete_stmnt = MySQLStatementBuilder(connection)
    res, row_count = delete_stmnt.delete(SUBPROJECTS_TABLE)\
        .where("project_id = %s AND id = %s", [project_id, subproject_id])\
        .execute(return_affected_rows=True)

    if row_count == 0:
        raise exc.SubProjectNotDeletedException

    return True


def db_get_user_subprojects_with_application_sid(con, user_id, application_sid) -> List[models.SubProject]:
    # Validate that the application is listed
    get_application(application_sid)

    # Get projects in which this user is a participant
    project_list = db_get_user_projects(con, user_id)
    project_id_list = []
    for project in project_list:
        project_id_list.append(project.id)

    if len(project_id_list) == 0:
        return []

    # Figure out which of those projects have an attached subproject with specified application SID.
    where_values = project_id_list.copy()
    where_values.append(application_sid)
    stmnt = MySQLStatementBuilder(con)
    rs = stmnt.select(SUBPROJECTS_TABLE, SUBPROJECT_COLUMNS)\
        .where(f"project_id IN {MySQLStatementBuilder.placeholder_array(len(project_id_list))} AND application_sid = %s",
               where_values)\
        .execute(fetch_type=FetchType.FETCH_ALL, dictionary=True)

    # Serialize & return
    subproject_list = []
    for res in rs:
        subproject_list.append(models.SubProject(**res))

    return subproject_list


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

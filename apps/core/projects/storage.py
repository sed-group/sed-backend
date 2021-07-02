from typing import List, Optional

from fastapi.logger import logger
from libs.mysqlutils import MySQLStatementBuilder, FetchType

from apps.core.applications.state import get_application
from apps.core.projects.models import Project, ProjectPost, ProjectListing, SubProjectPost, SubProject
from apps.core.projects.exceptions import *
from apps.core.users.storage import db_get_users_with_ids

PROJECTS_TABLE = 'projects'
PROJECTS_COLUMNS = ['id', 'name']
SUBPROJECTS_TABLE = 'projects_subprojects'
SUBPROJECT_COLUMNS = ['id', 'application_sid', 'project_id', 'native_project_id', 'owner_id']
PROJECTS_PARTICIPANTS_TABLE = 'projects_participants'
PROJECTS_PARTICIPANTS_COLUMNS = ['id', 'user_id', 'project_id', 'access_level']


def db_get_projects(connection, segment_length: int, index: int) -> List[ProjectListing]:
    mysql_statement = MySQLStatementBuilder(connection)
    projects = mysql_statement \
        .select('projects', PROJECTS_COLUMNS) \
        .limit(segment_length) \
        .offset(segment_length * index) \
        .execute(fetch_type=FetchType.FETCH_ALL, dictionary=True)

    return projects


def db_get_user_projects(connection, user_id: int, segment_length: int = 0, index: int = 0) -> List[ProjectListing]:
    participating_sql = MySQLStatementBuilder(connection)

    if index < 0:
        index = 0

    sql = participating_sql\
        .select(PROJECTS_TABLE, ['projects_participants.access_level', 'projects.name', 'projects.id']) \
        .inner_join(PROJECTS_PARTICIPANTS_TABLE, 'projects_participants.project_id = projects.id')\
        .where('projects_participants.user_id = %s', [user_id])
    if segment_length > 0:
        # Segment if segment length is specified
        sql = sql.limit(segment_length).offset(segment_length * index)

    rs = sql.execute(fetch_type=FetchType.FETCH_ALL, dictionary=True)

    project_list = []
    for result in rs:
        pl = ProjectListing(name=result['name'], access_level=result['access_level'], id=result['id'])
        project_list.append(pl)

    return project_list


def db_get_project(connection, project_id) -> Project:
    proj_sql = MySQLStatementBuilder(connection)
    proj_db_res = proj_sql \
        .select(PROJECTS_TABLE, PROJECTS_COLUMNS) \
        .where('id = %s', [project_id]) \
        .execute(fetch_type=FetchType.FETCH_ONE, dictionary=True)

    if proj_db_res is None:
        raise ProjectNotFoundException

    project = Project(id=proj_db_res['id'], name=proj_db_res['name'])

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
        raise NoParticipantsException()

    project.participants = db_get_users_with_ids(connection, participant_ids)

    return project


def db_post_project(connection, project: ProjectPost) -> Project:
    logger.debug('Adding new project:')
    logger.debug(project)

    project_sql = MySQLStatementBuilder(connection)
    project_cols = ['name']
    project_sql.insert(PROJECTS_TABLE, project_cols).set_values([project.name]).execute(return_affected_rows=True)
    project_id = project_sql.last_insert_id

    for participant_id in project.participants:
        access_level = project.participants_access.get(participant_id)
        db_add_participant(connection, project_id, participant_id, access_level, check_project_exists=False)

    return db_get_project(connection, project_id)


def db_delete_project(connection, project_id: int):
    logger.debug(f"Removing project: {project_id}")

    db_get_project(connection, project_id) # If the project does not exist, this raises the appropriate exception

    del_sql = MySQLStatementBuilder(connection)
    res, row_count = del_sql.delete(PROJECTS_TABLE).where('id = %s', [project_id]).execute(return_affected_rows=True)
    if row_count == 0:
        raise ProjectNotDeletedException("Unable to remove project")

    return True


def db_add_participant(connection, project_id, user_id, access_level, check_project_exists=True):
    if check_project_exists:
        db_get_project(connection, project_id)  # Raises exception if project does not exist

    participants_sql = MySQLStatementBuilder(connection)
    participants_cols = ['user_id', 'project_id', 'access_level']
    participants_sql.insert(PROJECTS_PARTICIPANTS_TABLE, participants_cols)\
        .set_values([user_id, project_id, access_level])\
        .execute()


def db_delete_participant(connection, project_id, user_id, check_project_exists=True):
    if check_project_exists:
        db_get_project(connection, project_id)  # Raises exception if project does not exist

    participants_sql = MySQLStatementBuilder(connection)
    res, row_count = participants_sql\
        .delete(PROJECTS_PARTICIPANTS_TABLE)\
        .where('project_id = %s AND user_id = %s', [project_id, user_id])\
        .execute(return_affected_rows=True)

    if row_count == 0:
        raise ParticipantChangeException("Failed to remove participant from project")

    return True


def db_put_name(connection, project_id, name):

    project = db_get_project(connection, project_id)    # Raises exception if project does not exist

    if project.name == name:
        return True

    project_sql = MySQLStatementBuilder(connection)
    res, row_count = project_sql\
        .update(PROJECTS_TABLE, "name = %s", [name]).where('id = %s', [project_id])\
        .execute(return_affected_rows=True)

    logger.debug(f"Affected rows: {row_count}")

    if row_count == 0:
        raise ProjectChangeException("Failed to update project information")

    return True


def db_post_subproject(connection, subproject: SubProjectPost, current_user_id: int, project_id: Optional[int] = None) \
        -> SubProject:

    if project_id is not None:
        db_get_project(connection, project_id)   # Raises exception if the project does not exist

    # Avoid duplicates
    try:
        duplicate = db_get_subproject_native(connection, subproject.application_sid, subproject.native_project_id)
        if duplicate is not None:
            raise SubProjectDuplicateException
    except SubProjectNotFoundException:
        insert_stmnt = MySQLStatementBuilder(connection)
        insert_stmnt\
            .insert(SUBPROJECTS_TABLE, ['application_sid', 'project_id', 'native_project_id', 'owner_id'])\
            .set_values([subproject.application_sid, project_id, subproject.native_project_id, current_user_id])\
            .execute()

        return db_get_subproject_native(connection, subproject.application_sid, subproject.native_project_id)


def db_get_subproject(connection, project_id, subproject_id) -> Optional[SubProject]:

    db_get_project(connection, project_id) # Raises exception if project does not exist

    select_stmnt = MySQLStatementBuilder(connection)
    res = select_stmnt\
        .select(SUBPROJECTS_TABLE, SUBPROJECT_COLUMNS)\
        .where("id = %s AND project_id = %s", [subproject_id, project_id])\
        .execute(fetch_type=FetchType.FETCH_ONE, dictionary=True)

    if res is None:
        raise SubProjectNotFoundException

    sub_project = SubProject(**res)

    return sub_project


def db_get_subproject_native(connection, application_sid, native_project_id) -> SubProject:
    get_application(application_sid)        # Raises exception of application does not exist

    select_stmnt = MySQLStatementBuilder(connection)
    res = select_stmnt\
        .select(SUBPROJECTS_TABLE, SUBPROJECT_COLUMNS)\
        .where("native_project_id = %s AND application_sid = %s", [native_project_id, application_sid])\
        .execute(fetch_type=FetchType.FETCH_ONE, dictionary=True)

    if res is None:
        raise SubProjectNotFoundException

    sub_project = SubProject(**res)

    return sub_project


def db_delete_subproject(connection, project_id, subproject_id):
    db_get_subproject(connection, project_id, subproject_id)  # Raises exception if project does not exist

    delete_stmnt = MySQLStatementBuilder(connection)
    res, row_count = delete_stmnt.delete(SUBPROJECTS_TABLE)\
        .where("project_id = %s AND id = %s", [project_id, subproject_id])\
        .execute(return_affected_rows=True)

    if row_count == 0:
        raise SubProjectNotDeletedException

    return


def db_get_user_subprojects_with_application_sid(con, user_id, application_sid) -> List[SubProject]:
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
        subproject_list.append(SubProject(**res))

    return subproject_list

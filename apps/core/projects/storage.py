from typing import List

from fastapi.logger import logger

from libs.mysqlutils import MySQLStatementBuilder, FetchType
from apps.core.projects.models import Project, AccessLevel, ProjectPost, ProjectListing
from apps.core.projects.exceptions import ProjectNotFoundException
from apps.core.users.storage import db_get_users_with_ids

PROJECTS_TABLE = 'projects'
PROJECTS_COLUMNS = ['id', 'name']
SUB_PROJECTS_TABLE = 'projects_sub'
SUB_PROJECT_COLUMNS = ['id', 'project_id', 'sub_project_id']
PROJECTS_PARTICIPANTS_TABLE = 'projects_participants'
PROJECTS_PARTICIPANTS_COLUMNS = ['id', 'user_id', 'project_id', 'access_type']


def db_get_projects(connection, segment_length: int, index: int) -> List[ProjectListing]:
    try:
        int(segment_length)
        int(index)
        if index < 0:
            index = 0
        if segment_length < 1:
            segment_length = 1
    except ValueError:
        raise TypeError

    mysql_statement = MySQLStatementBuilder(connection)
    projects = mysql_statement \
        .select('projects', PROJECTS_COLUMNS) \
        .limit(segment_length) \
        .offset(segment_length * index) \
        .execute(fetch_type=FetchType.FETCH_ALL, dictionary=True)

    return projects


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
        project.participants_access[participant_db['user_id']] = participant_db['access_type']

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
        access_type = project.participants_access.get(participant_id)
        participants_sql = MySQLStatementBuilder(connection)
        participants_cols = ['user_id', 'project_id', 'access_type']
        participants_sql.insert(PROJECTS_PARTICIPANTS_TABLE, participants_cols)\
            .set_values([participant_id, project_id, access_type])\
            .execute()

    return db_get_project(connection, project_id)


def db_add_participant(connection, project_id, users_to_access_dict) -> Project:
    project = db_get_project(connection, project_id)


def db_has_minimum_access(connection, project_id:int , user_id: int, minimum_level: AccessLevel):
    pass

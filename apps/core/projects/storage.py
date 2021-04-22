from typing import List

from libs.mysqlutils import MySQLStatementBuilder, FetchType

from apps.core.projects.models import Project, AccessLevel

PROJECTS_TABLE = 'projects'
PROJECTS_COLUMNS = ['id', 'name']
SUB_PROJECTS_TABLE = 'projects_sub'
SUB_PROJECT_COLUMNS = ['id', 'project_id', 'sub_project_id']
PROJECTS_PARTICIPANTS_TABLE = 'projects_participants'
PROJECTS_PARTICIPANTS_COLUMNS = ['id', 'user_id', 'project_id', 'access_type']


def db_get_projects(connection, segment_length: int, index: int) -> List[Project]:
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
    project = Project()
    project.name = 'Test'
    return project


def db_post_project(connection, project: Project) -> Project:
    return project


def db_has_minimum_access(connection, project_id:int , user_id: int, minimum_level: AccessLevel):
    pass

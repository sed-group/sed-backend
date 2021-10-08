from mysql.connector.pooling import PooledMySQLConnection
from fastapi.logger import logger

import apps.core.authentication.exceptions as auth_exceptions
from apps.core.users.storage import db_get_user_safe_with_id
import apps.core.projects.storage as proj_storage

import apps.cvs.exceptions as cvs_exceptions
import apps.cvs.models as models

from libs.mysqlutils import MySQLStatementBuilder, FetchType, Sort
from libs.datastructures.pagination import ListChunk

CVS_APPLICATION_SID = 'MOD.CVS'
CVS_TABLE = 'cvs_projects'
CVS_COLUMNS = ['id', 'name', 'description', 'owner_id', 'datetime_created']


def get_cvs_projects(db_connection: PooledMySQLConnection, segment_length: int, index: int,
                     user_id: int) -> ListChunk[models.CVSProject]:
    """
    Returns list of projects in which the current user is a participant.
    :param db_connection: Connection
    :param segment_length: Max amount of rows returned
    :param index: Offset, allowing pagination
    :param user_id: ID of current user
    :return:
    """

    logger.debug(f'Fetching CVS projects for user with id = {user_id}.')
    subproject_list = proj_storage.db_get_user_subprojects_with_application_sid(
        db_connection,
        user_id,
        CVS_APPLICATION_SID,
    )

    project_id_list = []
    for subproject in subproject_list:
        project_id_list.append(subproject.native_project_id)

    # Ensure that all projects in which the user is a participant is fetched, as well as all the projects in which the
    # user is an owner. This ensures that CVS projects which do not have an associated project also shows up in the
    # list, as long as the user is the owner. This is useful, because users might want to create CVS projects, without
    # having to create a 'Core Project'
    if len(project_id_list) > 0:
        where_statement = f'id IN {MySQLStatementBuilder.placeholder_array(len(project_id_list))} OR owner_id = %s'
    else:
        where_statement = f'owner_id = %s'

    where_values = project_id_list.copy()
    where_values.append(user_id)

    select_statement = MySQLStatementBuilder(db_connection)
    results = select_statement.select(CVS_TABLE, CVS_COLUMNS) \
        .where(where_statement, where_values) \
        .order_by(['name'], Sort.ASCENDING) \
        .limit(segment_length) \
        .offset(index * segment_length) \
        .execute(fetch_type=FetchType.FETCH_ALL, dictionary=True)

    project_list = []
    for result in results:
        project_list.append(populate_cvs_project(db_connection, result))  # Resource consuming for large batches

    count_statement = MySQLStatementBuilder(db_connection)
    result = count_statement.count(CVS_TABLE) \
        .where(where_statement, where_values) \
        .execute(fetch_type=FetchType.FETCH_ONE, dictionary=True)
    chunk = ListChunk[models.CVSProject](chunk=project_list, length_total=result['count'])

    return chunk


def get_cvs_project(db_connection: PooledMySQLConnection, project_id: int, user_id: int) -> models.CVSProject:
    select_statement = MySQLStatementBuilder(db_connection)
    result = select_statement \
        .select(CVS_TABLE, CVS_COLUMNS) \
        .where('id = %s', [project_id]) \
        .execute(fetch_type=FetchType.FETCH_ONE, dictionary=True)

    if result is None:
        raise cvs_exceptions.CVSProjectNotFoundException

    if result['owner_id'] != user_id:
        raise auth_exceptions.UnauthorizedOperationException

    return populate_cvs_project(db_connection, result)


def create_cvs_project(db_connection: PooledMySQLConnection, project: models.CVSProjectPost,
                       user_id: int) -> models.CVSProject:
    insert_statement = MySQLStatementBuilder(db_connection)
    insert_statement \
        .insert(table=CVS_TABLE, columns=['name', 'description', 'owner_id']) \
        .set_values([project.name, project.description, user_id]) \
        .execute(fetch_type=FetchType.FETCH_NONE)

    project_id = insert_statement.last_insert_id

    return get_cvs_project(db_connection, project_id, user_id)


def edit_cvs_project(db_connection: PooledMySQLConnection, project_id: int, user_id: int,
                     new_project: models.CVSProjectPost) -> models.CVSProject:
    old_project = get_cvs_project(db_connection, project_id, user_id)

    if (old_project.name, old_project.description) == (new_project.name, new_project.description):
        # No change
        return old_project

    # Updating
    update_statement = MySQLStatementBuilder(db_connection)
    update_statement.update(
        table=CVS_TABLE,
        set_statement='name = %s, description = %s',
        values=[new_project.name, new_project.description],
    )
    update_statement.where('id = %s', [project_id])
    _, rows = update_statement.execute(return_affected_rows=True)

    if rows == 0:
        raise cvs_exceptions.CVSProjectFailedToUpdateException

    return get_cvs_project(db_connection, project_id, user_id)


def delete_cvs_project(db_connection: PooledMySQLConnection, project_id: int, user_id: int) -> bool:
    select_statement = MySQLStatementBuilder(db_connection)
    result = select_statement \
        .select(CVS_TABLE, ['owner_id']) \
        .where('id = %s', [project_id]) \
        .execute(fetch_type=FetchType.FETCH_ONE, dictionary=True)

    if result is None:
        raise cvs_exceptions.CVSProjectNotFoundException

    if result['owner_id'] != user_id:
        raise auth_exceptions.UnauthorizedOperationException

    delete_statement = MySQLStatementBuilder(db_connection)
    result, rows = delete_statement.delete(CVS_TABLE) \
        .where('id = %s', [project_id]) \
        .execute(return_affected_rows=True)

    if rows == 0:
        raise cvs_exceptions.CVSProjectFailedDeletionException

    return True


def populate_cvs_project(db_connection: PooledMySQLConnection, database_result) -> models.CVSProject:
    return models.CVSProject(
        id=database_result['id'],
        name=database_result['name'],
        description=database_result['description'],
        owner=db_get_user_safe_with_id(db_connection, database_result['owner_id']),
        datetime_created=database_result['datetime_created'],
    )

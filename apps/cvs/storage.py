import typing

from mysql.connector.pooling import PooledMySQLConnection
from fastapi.logger import logger
from typing import Callable
from pydantic import BaseModel

import apps.core.authentication.exceptions as auth_exceptions
from apps.core.users.storage import db_get_user_safe_with_id
import apps.core.projects.storage as proj_storage

import apps.cvs.exceptions as cvs_exceptions
import apps.cvs.models as models

from libs.mysqlutils import MySQLStatementBuilder, FetchType, Sort
from libs.datastructures.pagination import ListChunk

CVS_APPLICATION_SID = 'MOD.CVS'
CVS_PROJECT_TABLE = 'cvs_projects'
CVS_PROJECT_COLUMNS = ['id', 'name', 'description', 'owner_id', 'datetime_created']
CVS_VCS_TABLE = 'cvs_vcss'
CVS_VCS_COLUMNS = ['id', 'name', 'description', 'project_id', 'datetime_created', 'year_from', 'year_to']
CVS_VCS_VALUE_DRIVER_TABLE = 'cvs_vcs_value_drivers'
CVS_VCS_VALUE_DRIVER_COLUMNS = ['id', 'name', 'project_id']


# ======================================================================================================================
# CVS projects
# ======================================================================================================================

def get_all_cvs_project(db_connection: PooledMySQLConnection, user_id: int) -> ListChunk[models.CVSProject]:
    """ Returns list of all projects in which the current user is a participant. """

    logger.debug(f'Fetching all CVS projects for user with id = {user_id}.')

    where_statement = f'owner_id = %s'
    where_values = [user_id]

    select_statement = MySQLStatementBuilder(db_connection)
    results = select_statement.select(CVS_PROJECT_TABLE, CVS_PROJECT_COLUMNS) \
        .where(where_statement, where_values) \
        .order_by(['name'], Sort.ASCENDING) \
        .execute(fetch_type=FetchType.FETCH_ALL, dictionary=True)

    project_list = []
    for result in results:
        project_list.append(populate_cvs_project(db_connection, result))  # Resource consuming for large batches

    count_statement = MySQLStatementBuilder(db_connection)
    result = count_statement.count(CVS_PROJECT_TABLE) \
        .where(where_statement, where_values) \
        .execute(fetch_type=FetchType.FETCH_ONE, dictionary=True)
    chunk = ListChunk[models.CVSProject](chunk=project_list, length_total=result['count'])

    return chunk


def get_segment_cvs_project(db_connection: PooledMySQLConnection, index: int, segment_length: int,
                            user_id: int) -> ListChunk[models.CVSProject]:
    """ Returns segment of projects in which the current user is a participant. """

    logger.debug(f'Fetching CVS projects for user with id = {user_id}.')

    where_statement = f'owner_id = %s'
    where_values = [user_id]

    select_statement = MySQLStatementBuilder(db_connection)
    results = select_statement.select(CVS_PROJECT_TABLE, CVS_PROJECT_COLUMNS) \
        .where(where_statement, where_values) \
        .order_by(['name'], Sort.ASCENDING) \
        .limit(segment_length) \
        .offset(index * segment_length) \
        .execute(fetch_type=FetchType.FETCH_ALL, dictionary=True)

    project_list = []
    for result in results:
        project_list.append(populate_cvs_project(db_connection, result))  # Resource consuming for large batches

    count_statement = MySQLStatementBuilder(db_connection)
    result = count_statement.count(CVS_PROJECT_TABLE) \
        .where(where_statement, where_values) \
        .execute(fetch_type=FetchType.FETCH_ONE, dictionary=True)
    chunk = ListChunk[models.CVSProject](chunk=project_list, length_total=result['count'])

    return chunk


def get_cvs_project(db_connection: PooledMySQLConnection, project_id: int, user_id: int) -> models.CVSProject:
    print('-> project 1')
    select_statement = MySQLStatementBuilder(db_connection)
    print('-> project 2')
    result = select_statement \
        .select(CVS_PROJECT_TABLE, CVS_PROJECT_COLUMNS) \
        .where('id = %s', [project_id]) \
        .execute(fetch_type=FetchType.FETCH_ONE, dictionary=True)
    print('-> project 3')

    if result is None:
        raise cvs_exceptions.CVSProjectNotFoundException
    print('-> project 4')

    if result['owner_id'] != user_id:
        raise auth_exceptions.UnauthorizedOperationException
    print('-> project 5')

    return populate_cvs_project(db_connection, result)


def create_cvs_project(db_connection: PooledMySQLConnection, project: models.CVSProjectPost,
                       user_id: int) -> models.CVSProject:
    insert_statement = MySQLStatementBuilder(db_connection)
    insert_statement \
        .insert(table=CVS_PROJECT_TABLE, columns=['name', 'description', 'owner_id']) \
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
        table=CVS_PROJECT_TABLE,
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
        .select(CVS_PROJECT_TABLE, ['owner_id']) \
        .where('id = %s', [project_id]) \
        .execute(fetch_type=FetchType.FETCH_ONE, dictionary=True)

    if result is None:
        raise cvs_exceptions.CVSProjectNotFoundException

    if result['owner_id'] != user_id:
        raise auth_exceptions.UnauthorizedOperationException

    delete_statement = MySQLStatementBuilder(db_connection)
    result, rows = delete_statement.delete(CVS_PROJECT_TABLE) \
        .where('id = %s', [project_id]) \
        .execute(return_affected_rows=True)

    if rows == 0:
        raise cvs_exceptions.CVSProjectFailedDeletionException

    return True


def populate_cvs_project(db_connection: PooledMySQLConnection, db_result) -> models.CVSProject:
    print('-> project 6')
    print(f'{db_result = }')
    return models.CVSProject(
        id=db_result['id'],
        name=db_result['name'],
        description=db_result['description'],
        owner=db_get_user_safe_with_id(db_connection, db_result['owner_id']),
        datetime_created=db_result['datetime_created'],
    )


# ======================================================================================================================
# VCS (Value Creation Strategy)
# ======================================================================================================================

def get_all_vcs(db_connection: PooledMySQLConnection, project_id: int, user_id: int) -> ListChunk[models.VCS]:
    """ Returns a list of all VCSs of a project. """

    logger.debug(f'Fetching all VCSs for project with id = {project_id} (user id = {user_id}).')

    where_values = [project_id]
    where_statement = f'project_id = %s'

    select_statement = MySQLStatementBuilder(db_connection)
    results = select_statement.select(CVS_VCS_TABLE, CVS_VCS_COLUMNS) \
        .where(where_statement, where_values) \
        .order_by(['id'], Sort.ASCENDING) \
        .execute(fetch_type=FetchType.FETCH_ALL, dictionary=True)

    vcs_list = []
    for result in results:
        vcs_list.append(populate_vcs(db_connection, result, project_id, user_id))

    count_statement = MySQLStatementBuilder(db_connection)
    result = count_statement.count(CVS_VCS_TABLE) \
        .where(where_statement, where_values) \
        .execute(fetch_type=FetchType.FETCH_ONE, dictionary=True)
    chunk = ListChunk[models.VCS](chunk=vcs_list, length_total=result['count'])

    return chunk


def get_segment_vcs(db_connection: PooledMySQLConnection, project_id: int, segment_length: int, index: int,
                    user_id: int) -> ListChunk[models.VCS]:
    """ Returns a list of a selected segment of VCSs of a project. """

    logger.debug(f'Fetching VCS segment for project with id = {project_id} (user id = {user_id}).')

    where_values = [project_id]
    where_statement = f'project_id = %s'

    select_statement = MySQLStatementBuilder(db_connection)
    results = select_statement.select(CVS_VCS_TABLE, CVS_VCS_COLUMNS) \
        .where(where_statement, where_values) \
        .order_by(['id'], Sort.ASCENDING) \
        .limit(segment_length) \
        .offset(index * segment_length) \
        .execute(fetch_type=FetchType.FETCH_ALL, dictionary=True)

    vcs_list = []
    for result in results:
        vcs_list.append(populate_vcs(db_connection, result, project_id, user_id))

    count_statement = MySQLStatementBuilder(db_connection)
    result = count_statement.count(CVS_VCS_TABLE) \
        .where(where_statement, where_values) \
        .execute(fetch_type=FetchType.FETCH_ONE, dictionary=True)
    chunk = ListChunk[models.VCS](chunk=vcs_list, length_total=result['count'])

    return chunk


def get_vcs(db_connection: PooledMySQLConnection, vcs_id: int, project_id: int, user_id: int) -> models.VCS:
    select_statement = MySQLStatementBuilder(db_connection)
    result = select_statement \
        .select(CVS_VCS_TABLE, CVS_VCS_COLUMNS) \
        .where('id = %s', [vcs_id]) \
        .execute(fetch_type=FetchType.FETCH_ONE, dictionary=True)

    if result is None:
        raise cvs_exceptions.VCSNotFoundException

    if result['project_id'] != project_id:
        raise auth_exceptions.UnauthorizedOperationException

    return populate_vcs(db_connection, result, project_id, user_id)


def create_vcs(db_connection: PooledMySQLConnection, vcs_post: models.VCSPost, project_id: int,
               user_id: int) -> models.VCS:
    get_cvs_project(db_connection, project_id, user_id)  # performs checks for existing project and correct user

    insert_statement = MySQLStatementBuilder(db_connection)
    insert_statement \
        .insert(table=CVS_VCS_TABLE, columns=['name', 'description', 'project_id', 'year_from', 'year_to']) \
        .set_values([vcs_post.name, vcs_post.description, project_id, vcs_post.year_from, vcs_post.year_to]) \
        .execute(fetch_type=FetchType.FETCH_NONE)
    vcs_id = insert_statement.last_insert_id

    return get_vcs(db_connection, vcs_id, project_id, user_id)


def edit_vcs(db_connection: PooledMySQLConnection, vcs_id: int, project_id: int, user_id: int,
             new_vcs: models.VCSPost) -> models.VCS:
    old_vcs = get_vcs(db_connection, vcs_id, project_id, user_id)

    o = (old_vcs.name, old_vcs.description, old_vcs.year_from, old_vcs.year_to)
    n = (new_vcs.name, new_vcs.description, new_vcs.year_from, new_vcs.year_to)
    if o == n:  # No change
        return old_vcs

    # Updating
    update_statement = MySQLStatementBuilder(db_connection)
    update_statement.update(
        table=CVS_VCS_TABLE,
        set_statement='name = %s, description = %s, year_from = %s, year_to = %s',
        values=[new_vcs.name, new_vcs.description, new_vcs.year_from, new_vcs.year_to],
    )
    update_statement.where('id = %s', [project_id])
    _, rows = update_statement.execute(return_affected_rows=True)

    if rows == 0:
        raise cvs_exceptions.VCSFailedToUpdateException

    return get_vcs(db_connection, vcs_id, project_id, user_id)


def delete_vcs(db_connection: PooledMySQLConnection, vcs_id: int, project_id: int, user_id: int) -> bool:
    select_statement = MySQLStatementBuilder(db_connection)

    result = select_statement \
        .select(CVS_VCS_TABLE, CVS_VCS_COLUMNS) \
        .where('id = %s', [vcs_id]) \
        .execute(fetch_type=FetchType.FETCH_ONE, dictionary=True)

    if result is None:
        raise cvs_exceptions.VCSNotFoundException

    if result['project_id'] != project_id:
        raise auth_exceptions.UnauthorizedOperationException

    get_cvs_project(db_connection, project_id, user_id)  # performs checks for existing project and correct user

    delete_statement = MySQLStatementBuilder(db_connection)
    result, rows = delete_statement.delete(CVS_VCS_TABLE) \
        .where('id = %s', [vcs_id]) \
        .execute(return_affected_rows=True)

    if rows == 0:
        raise cvs_exceptions.VCSFailedDeletionException

    return True


def populate_vcs(db_connection: PooledMySQLConnection, db_result, project_id: int, user_id: int) -> models.VCS:
    return models.VCS(
        id=db_result['id'],
        name=db_result['name'],
        description=db_result['description'],
        project=get_cvs_project(db_connection, project_id=project_id, user_id=user_id),
        datetime_created=db_result['datetime_created'],
        year_from=db_result['year_from'],
        year_to=db_result['year_to'],
    )


# ======================================================================================================================
# VCS Value driver
# ======================================================================================================================

def get_all_value_driver(db_connection: PooledMySQLConnection, project_id: int,
                         user_id: int) -> ListChunk[models.VCSValueDriver]:
    """ Returns a list of all value drivers of a project. """

    logger.debug(f'Fetching all value drivers for project with id = {project_id} (user id = {user_id}).')

    where_values = [project_id]
    where_statement = f'project_id = %s'

    select_statement = MySQLStatementBuilder(db_connection)
    results = select_statement.select(CVS_VCS_VALUE_DRIVER_TABLE, CVS_VCS_VALUE_DRIVER_COLUMNS) \
        .where(where_statement, where_values) \
        .order_by(['id'], Sort.ASCENDING) \
        .execute(fetch_type=FetchType.FETCH_ALL, dictionary=True)

    value_driver_list = []
    for result in results:
        value_driver_list.append(populate_value_driver(db_connection, result, project_id, user_id))

    count_statement = MySQLStatementBuilder(db_connection)
    result = count_statement.count(CVS_VCS_VALUE_DRIVER_TABLE) \
        .where(where_statement, where_values) \
        .execute(fetch_type=FetchType.FETCH_ONE, dictionary=True)
    chunk = ListChunk[models.VCSValueDriver](chunk=value_driver_list, length_total=result['count'])

    return chunk


def get_value_driver(db_connection: PooledMySQLConnection, value_driver_id: int, project_id: int,
                     user_id: int) -> models.VCSValueDriver:
    select_statement = MySQLStatementBuilder(db_connection)
    result = select_statement \
        .select(CVS_VCS_VALUE_DRIVER_TABLE, CVS_VCS_VALUE_DRIVER_COLUMNS) \
        .where('id = %s', [value_driver_id]) \
        .execute(fetch_type=FetchType.FETCH_ONE, dictionary=True)

    if result is None:
        raise cvs_exceptions.ValueDriverNotFoundException

    if result['project_id'] != project_id:
        raise auth_exceptions.UnauthorizedOperationException

    return populate_value_driver(db_connection, result, project_id, user_id)


def create_value_driver(db_connection: PooledMySQLConnection, value_driver_post: models.VCSValueDriverPost,
                        project_id: int, user_id: int) -> models.VCSValueDriver:
    get_cvs_project(db_connection, project_id, user_id)  # performs checks for existing project and correct user

    insert_statement = MySQLStatementBuilder(db_connection)
    insert_statement \
        .insert(table=CVS_VCS_VALUE_DRIVER_TABLE, columns=['name', 'project_id']) \
        .set_values([value_driver_post.name, project_id]) \
        .execute(fetch_type=FetchType.FETCH_NONE)
    value_driver_id = insert_statement.last_insert_id

    return get_value_driver(db_connection, value_driver_id, project_id, user_id)


def edit_value_driver(db_connection: PooledMySQLConnection, value_driver_id: int, project_id: int, user_id: int,
                      new_value_driver: models.VCSValueDriverPost) -> models.VCSValueDriver:
    old_value_driver = get_value_driver(db_connection, value_driver_id, project_id, user_id)

    if old_value_driver.name == new_value_driver.name:  # No change
        return old_value_driver

    # Updating
    update_statement = MySQLStatementBuilder(db_connection)
    update_statement.update(
        table=CVS_VCS_VALUE_DRIVER_TABLE,
        set_statement='name = %s',
        values=[new_value_driver.name],
    )
    update_statement.where('id = %s', [project_id])
    _, rows = update_statement.execute(return_affected_rows=True)

    if rows == 0:
        raise cvs_exceptions.ValueDriverFailedToUpdateException

    return get_value_driver(db_connection, value_driver_id, project_id, user_id)


def delete_value_driver(db_connection: PooledMySQLConnection, value_driver_id: int, project_id: int,
                        user_id: int) -> bool:
    get_cvs_project(db_connection, project_id, user_id)  # performs checks for existing project and correct user

    select_statement = MySQLStatementBuilder(db_connection)
    result = select_statement \
        .select(CVS_VCS_VALUE_DRIVER_TABLE, CVS_VCS_VALUE_DRIVER_COLUMNS) \
        .where('id = %s', [value_driver_id]) \
        .execute(fetch_type=FetchType.FETCH_ONE, dictionary=True)

    if result is None:
        raise cvs_exceptions.ValueDriverNotFoundException

    if result['project_id'] != project_id:
        raise auth_exceptions.UnauthorizedOperationException

    delete_statement = MySQLStatementBuilder(db_connection)
    result, rows = delete_statement.delete(CVS_VCS_VALUE_DRIVER_TABLE) \
        .where('id = %s', [value_driver_id]) \
        .execute(return_affected_rows=True)

    if rows == 0:
        raise cvs_exceptions.ValueDriverFailedDeletionException

    return True


def populate_value_driver(db_connection: PooledMySQLConnection, db_result, project_id: int,
                          user_id: int) -> models.VCSValueDriver:
    return models.VCSValueDriver(
        id=db_result['id'],
        name=db_result['name'],
        project=get_cvs_project(db_connection, project_id=project_id, user_id=user_id),
    )

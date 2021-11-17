import time

from mysql.connector.pooling import PooledMySQLConnection
from fastapi.logger import logger
from typing import List

import apps.core.authentication.exceptions as auth_exceptions
from apps.core.users.storage import db_get_user_safe_with_id

import apps.cvs.exceptions as cvs_exceptions
import apps.cvs.implementation as impl
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

CVS_VCS_SUBPROCESS_TABLE = 'cvs_vcs_subprocesses'
CVS_VCS_SUBPROCESS_COLUMNS = ['id', 'name', 'parent_process_id', 'project_id']

CVS_VCS_TABLE_ROWS_TABLE = 'cvs_vcs_table_rows'
CVS_VCS_TABLE_ROWS_COLUMNS = ['id', 'vcs_id', 'isoprocess_id', 'subprocess_id', 'stakeholder',
                              'stakeholder_expectations']

CVS_VCS_STAKEHOLDER_NEED_TABLE = 'cvs_vcs_stakeholder_needs'
CVS_VCS_STAKEHOLDER_NEED_COLUMNS = ['id', 'vcs_row_id', 'need', 'stakeholder_expectations', 'rank_weight']

CVS_VCS_NEEDS_DRIVERS_MAP_TABLE = 'cvs_vcs_needs_divers_map'
CVS_VCS_NEEDS_DRIVERS_MAP_COLUMNS = ['id', 'stakeholder_need_id', 'value_driver_id']


# ======================================================================================================================
# CVS projects
# ======================================================================================================================

def get_all_cvs_project(db_connection: PooledMySQLConnection, user_id: int) -> ListChunk[models.CVSProject]:
    logger.debug(f'Fetching all CVS projects for user with id={user_id}.')

    where_statement = f'owner_id = %s'
    where_values = [user_id]

    select_statement = MySQLStatementBuilder(db_connection)
    results = select_statement.select(CVS_PROJECT_TABLE, CVS_PROJECT_COLUMNS) \
        .where(where_statement, where_values) \
        .order_by(['name'], Sort.ASCENDING) \
        .execute(fetch_type=FetchType.FETCH_ALL, dictionary=True)

    project_list = []
    for result in results:
        project_list.append(populate_cvs_project(db_connection, result))

    count_statement = MySQLStatementBuilder(db_connection)
    result = count_statement.count(CVS_PROJECT_TABLE) \
        .where(where_statement, where_values) \
        .execute(fetch_type=FetchType.FETCH_ONE, dictionary=True)
    chunk = ListChunk[models.CVSProject](chunk=project_list, length_total=result['count'])

    return chunk


def get_segment_cvs_project(db_connection: PooledMySQLConnection, index: int, segment_length: int,
                            user_id: int) -> ListChunk[models.CVSProject]:
    logger.debug(f'Fetching segment of CVS projects for user with id={user_id}.')

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
        project_list.append(populate_cvs_project(db_connection, result))

    count_statement = MySQLStatementBuilder(db_connection)
    result = count_statement.count(CVS_PROJECT_TABLE) \
        .where(where_statement, where_values) \
        .execute(fetch_type=FetchType.FETCH_ONE, dictionary=True)
    chunk = ListChunk[models.CVSProject](chunk=project_list, length_total=result['count'])

    return chunk


def get_cvs_project(db_connection: PooledMySQLConnection, project_id: int, user_id: int) -> models.CVSProject:
    logger.debug(f'Fetching CVS project with id={project_id}.')

    select_statement = MySQLStatementBuilder(db_connection)
    result = select_statement \
        .select(CVS_PROJECT_TABLE, CVS_PROJECT_COLUMNS) \
        .where('id = %s', [project_id]) \
        .execute(fetch_type=FetchType.FETCH_ONE, dictionary=True)

    if result is None:
        raise cvs_exceptions.CVSProjectNotFoundException

    if result['owner_id'] != user_id:
        raise auth_exceptions.UnauthorizedOperationException

    return populate_cvs_project(db_connection, result)


def create_cvs_project(db_connection: PooledMySQLConnection, project: models.CVSProjectPost,
                       user_id: int) -> models.CVSProject:
    logger.debug(f'Creating a CVS project for user with id={user_id}.')

    insert_statement = MySQLStatementBuilder(db_connection)
    insert_statement \
        .insert(table=CVS_PROJECT_TABLE, columns=['name', 'description', 'owner_id']) \
        .set_values([project.name, project.description, user_id]) \
        .execute(fetch_type=FetchType.FETCH_NONE)

    project_id = insert_statement.last_insert_id

    return get_cvs_project(db_connection, project_id, user_id)


def edit_cvs_project(db_connection: PooledMySQLConnection, project_id: int, user_id: int,
                     new_project: models.CVSProjectPost) -> models.CVSProject:
    logger.debug(f'Editing CVS project with id={project_id}.')

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
    logger.debug(f'Deleting CVS project with id={project_id}.')

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
    _, rows = delete_statement.delete(CVS_PROJECT_TABLE) \
        .where('id = %s', [project_id]) \
        .execute(return_affected_rows=True)

    if rows == 0:
        raise cvs_exceptions.CVSProjectFailedDeletionException

    return True


def populate_cvs_project(db_connection: PooledMySQLConnection, db_result) -> models.CVSProject:
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
    logger.debug(f'Fetching all VCSs for project with id={project_id}.')

    where_statement = f'project_id = %s'
    where_values = [project_id]

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
    logger.debug(f'Fetching VCS segment for project with id={project_id}.')

    where_statement = f'project_id = %s'
    where_values = [project_id]

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
    logger.debug(f'Fetching VCS with id={vcs_id}.')

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
    logger.debug(f'Creating a VCS in project with id={project_id}.')

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
    logger.debug(f'Editing VCS with id={vcs_id}.')

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
    update_statement.where('id = %s', [vcs_id])
    _, rows = update_statement.execute(return_affected_rows=True)

    if rows == 0:
        raise cvs_exceptions.VCSFailedToUpdateException

    return get_vcs(db_connection, vcs_id, project_id, user_id)


def delete_vcs(db_connection: PooledMySQLConnection, vcs_id: int, project_id: int, user_id: int) -> bool:
    logger.debug(f'Deleting VCS with id={vcs_id}.')

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
    _, rows = delete_statement.delete(CVS_VCS_TABLE) \
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
    logger.debug(f'Fetching all value drivers for project with id={project_id}.')

    where_statement = f'project_id = %s'
    where_values = [project_id]

    select_statement = MySQLStatementBuilder(db_connection)
    results = select_statement \
        .select(CVS_VCS_VALUE_DRIVER_TABLE, CVS_VCS_VALUE_DRIVER_COLUMNS) \
        .where(where_statement, where_values) \
        .order_by(['id'], Sort.ASCENDING) \
        .execute(fetch_type=FetchType.FETCH_ALL, dictionary=True)

    value_driver_list = []
    for result in results:
        value_driver_list.append(populate_value_driver(db_connection, result, project_id, user_id))

    count_statement = MySQLStatementBuilder(db_connection)
    result = count_statement \
        .count(CVS_VCS_VALUE_DRIVER_TABLE) \
        .where(where_statement, where_values) \
        .execute(fetch_type=FetchType.FETCH_ONE, dictionary=True)
    chunk = ListChunk[models.VCSValueDriver](chunk=value_driver_list, length_total=result['count'])

    return chunk


def get_value_driver(db_connection: PooledMySQLConnection, value_driver_id: int, project_id: int,
                     user_id: int) -> models.VCSValueDriver:
    logger.debug(f'Fetching value driver with id={value_driver_id}.')

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
    logger.debug(f'Creating a value driver in project with id={project_id}.')

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
    logger.debug(f'Editing value driver with id={value_driver_id}.')

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
    update_statement.where('id = %s', [value_driver_id])
    _, rows = update_statement.execute(return_affected_rows=True)

    if rows == 0:
        raise cvs_exceptions.ValueDriverFailedToUpdateException

    return get_value_driver(db_connection, value_driver_id, project_id, user_id)


def delete_value_driver(db_connection: PooledMySQLConnection, value_driver_id: int, project_id: int,
                        user_id: int) -> bool:
    logger.debug(f'Deleting value driver with id={value_driver_id}.')

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
    _, rows = delete_statement.delete(CVS_VCS_VALUE_DRIVER_TABLE) \
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


# ======================================================================================================================
# VCS ISO Processes
# ======================================================================================================================


def get_all_iso_process() -> ListChunk[models.VCSISOProcess]:
    logger.debug(f'Fetching all ISO processes.')

    iso_processes = [process.value for process in models.VCSISOProcesses]
    chunk = ListChunk[models.VCSISOProcess](chunk=iso_processes, length_total=len(iso_processes))

    return chunk


def get_iso_process(iso_process_id: int) -> models.VCSISOProcess:
    logger.debug(f'Fetching ISO process with id={iso_process_id}.')

    for p in models.VCSISOProcesses:
        if p.value.id == iso_process_id:
            return p.value

    raise cvs_exceptions.ISOProcessNotFoundException


# ======================================================================================================================
# VCS Subprocesses
# ======================================================================================================================

def get_all_subprocess(db_connection: PooledMySQLConnection, project_id: int,
                       user_id: int) -> ListChunk[models.VCSSubprocess]:
    logger.debug(f'Fetching all subprocesses for project with id={project_id}.')

    where_statement = f'project_id = %s'
    where_values = [project_id]

    select_statement = MySQLStatementBuilder(db_connection)
    results = select_statement \
        .select(CVS_VCS_SUBPROCESS_TABLE, CVS_VCS_SUBPROCESS_COLUMNS) \
        .where(where_statement, where_values) \
        .order_by(['id'], Sort.ASCENDING) \
        .execute(fetch_type=FetchType.FETCH_ALL, dictionary=True)

    subprocess_list = [populate_subprocess(db_connection, result, project_id, user_id) for result in results]

    count_statement = MySQLStatementBuilder(db_connection)
    result = count_statement \
        .count(CVS_VCS_SUBPROCESS_TABLE) \
        .where(where_statement, where_values) \
        .execute(fetch_type=FetchType.FETCH_ONE, dictionary=True)
    chunk = ListChunk[models.VCSSubprocess](chunk=subprocess_list, length_total=result['count'])

    return chunk


def get_subprocess(db_connection: PooledMySQLConnection, subprocess_id: int, project_id: int,
                   user_id: int) -> models.VCSSubprocess:
    logger.debug(f'Fetching subprocess with id={subprocess_id}.')

    select_statement = MySQLStatementBuilder(db_connection)
    result = select_statement \
        .select(CVS_VCS_SUBPROCESS_TABLE, CVS_VCS_SUBPROCESS_COLUMNS) \
        .where('id = %s', [subprocess_id]) \
        .execute(fetch_type=FetchType.FETCH_ONE, dictionary=True)

    if result is None:
        raise cvs_exceptions.SubprocessNotFoundException

    if result['project_id'] != project_id:
        raise auth_exceptions.UnauthorizedOperationException

    return populate_subprocess(db_connection, result, project_id, user_id)


def create_subprocess(db_connection: PooledMySQLConnection, subprocess_post: models.VCSSubprocessPost,
                      project_id: int, user_id: int) -> models.VCSSubprocess:
    logger.debug(f'Creating a subprocesses in project with id={project_id}.')

    get_cvs_project(db_connection, project_id, user_id)  # performs checks for existing project and correct user
    get_iso_process(subprocess_post.parent_process_id)  # performs checks for existing iso process

    insert_statement = MySQLStatementBuilder(db_connection)
    insert_statement \
        .insert(table=CVS_VCS_SUBPROCESS_TABLE, columns=['name', 'parent_process_id', 'project_id']) \
        .set_values([subprocess_post.name, subprocess_post.parent_process_id, project_id]) \
        .execute(fetch_type=FetchType.FETCH_NONE)
    subprocess_id = insert_statement.last_insert_id

    return get_subprocess(db_connection, subprocess_id, project_id, user_id)


def edit_subprocess(db_connection: PooledMySQLConnection, subprocess_id: int, project_id: int, user_id: int,
                    new_subprocess: models.VCSSubprocessPost) -> models.VCSSubprocess:
    logger.debug(f'Editing subprocesses with id={subprocess_id}.')

    old_subprocess = get_subprocess(db_connection, subprocess_id, project_id, user_id)
    o = (old_subprocess.name, old_subprocess.parent_process.id)
    n = (new_subprocess.name, new_subprocess.parent_process_id)
    if o == n:  # No change
        return old_subprocess

    get_cvs_project(db_connection, project_id, user_id)  # performs checks for existing project and correct user
    get_iso_process(new_subprocess.parent_process_id)  # performs checks for existing iso process

    # Updating
    update_statement = MySQLStatementBuilder(db_connection)
    update_statement.update(
        table=CVS_VCS_SUBPROCESS_TABLE,
        set_statement='name = %s, parent_process_id = %s',
        values=[new_subprocess.name, new_subprocess.parent_process_id],
    )
    update_statement.where('id = %s', [subprocess_id])
    _, rows = update_statement.execute(return_affected_rows=True)

    if rows == 0:
        raise cvs_exceptions.SubprocessFailedToUpdateException

    return get_subprocess(db_connection, subprocess_id, project_id, user_id)


def delete_subprocess(db_connection: PooledMySQLConnection, subprocess_id: int, project_id: int,
                      user_id: int) -> bool:
    logger.debug(f'Deleting subprocesses with id={subprocess_id}.')

    get_cvs_project(db_connection, project_id, user_id)  # performs checks for existing project and correct user

    select_statement = MySQLStatementBuilder(db_connection)
    result = select_statement \
        .select(CVS_VCS_SUBPROCESS_TABLE, CVS_VCS_SUBPROCESS_COLUMNS) \
        .where('id = %s', [subprocess_id]) \
        .execute(fetch_type=FetchType.FETCH_ONE, dictionary=True)

    if result is None:
        raise cvs_exceptions.SubprocessNotFoundException

    if result['project_id'] != project_id:
        raise auth_exceptions.UnauthorizedOperationException

    delete_statement = MySQLStatementBuilder(db_connection)
    _, rows = delete_statement.delete(CVS_VCS_SUBPROCESS_TABLE) \
        .where('id = %s', [subprocess_id]) \
        .execute(return_affected_rows=True)

    if rows == 0:
        raise cvs_exceptions.SubprocessFailedDeletionException

    return True


def populate_subprocess(db_connection: PooledMySQLConnection, db_result, project_id: int,
                        user_id: int) -> models.VCSSubprocess:
    return models.VCSSubprocess(
        id=db_result['id'],
        name=db_result['name'],
        parent_process=get_iso_process(db_result['parent_process_id']),
        project=get_cvs_project(db_connection, project_id, user_id)
    )


# ======================================================================================================================
# VCS Table Row
# ======================================================================================================================

def get_all_vcs_table_rows(db_connection: PooledMySQLConnection, vcs_id: int, project_id: int,
                           user_id: int) -> ListChunk[models.VCSTableRow]:
    logger.debug(f'Fetching all VCS table rows for VCS with id={vcs_id}.')

    vcs = impl.get_vcs(vcs_id, project_id, user_id)  # perfoming necessary controls

    where_statement = f'vcs_id = %s'
    where_values = [vcs_id]

    select_statement = MySQLStatementBuilder(db_connection)
    results = select_statement \
        .select(CVS_VCS_TABLE_ROWS_TABLE, CVS_VCS_TABLE_ROWS_COLUMNS) \
        .where(where_statement, where_values) \
        .order_by(['id'], Sort.ASCENDING) \
        .execute(fetch_type=FetchType.FETCH_ALL, dictionary=True)

    table_row_list = [populate_vcs_table_row(result, vcs, project_id, user_id) for result in results]

    return ListChunk[models.VCSTableRow](chunk=table_row_list, length_total=len(table_row_list))


def get_vcs_table_row(db_connection: PooledMySQLConnection, table_row_id: int, vcs_id: int, project_id: int,
                      user_id: int) -> models.VCSTableRow:
    logger.debug(f'Fetching VCS table row with id={table_row_id}.')

    select_statement = MySQLStatementBuilder(db_connection)
    result = select_statement \
        .select(CVS_VCS_TABLE_ROWS_TABLE, CVS_VCS_TABLE_ROWS_COLUMNS) \
        .where('id = %s', [table_row_id]) \
        .execute(fetch_type=FetchType.FETCH_ONE, dictionary=True)

    if result is None:
        raise cvs_exceptions.VCSTableRowNotFoundException

    if result['vcs_id'] != vcs_id:
        raise auth_exceptions.UnauthorizedOperationException

    vcs = impl.get_vcs(vcs_id, project_id, user_id)  # perfoming necessary controls

    return populate_vcs_table_row(result, vcs, project_id, user_id)


def create_vcs_table_row(db_connection: PooledMySQLConnection, new_row: models.VCSTableRowPost, vcs_id: int,
                         project_id: int, user_id: int) -> models.VCSTableRow:
    logger.debug(f'Creating a table row in VCS with id={vcs_id}.')

    get_cvs_project(db_connection, project_id, user_id)  # perfoming necessary controls

    iso_process_id, subprocess_id = None, None
    if (new_row.iso_process_id is None) and (new_row.subprocess_id is None):
        raise cvs_exceptions.VCSTableRowProcessNotProvided

    elif (new_row.iso_process_id is not None) and (new_row.subprocess_id is not None):
        raise cvs_exceptions.VCSTableRowProcessAmbiguity

    elif new_row.iso_process_id is not None:  # ISO process was the provided one
        iso_process_id = impl.get_iso_process(new_row.iso_process_id).id  # performing controls

    else:  # subprocess was the provided one
        subprocess_id = impl.get_subprocess(new_row.subprocess_id, project_id, user_id).id  # performing controls

    columns = ['vcs_id', 'isoprocess_id', 'subprocess_id', 'stakeholder', 'stakeholder_expectations']
    values = [vcs_id, iso_process_id, subprocess_id, new_row.stakeholder, new_row.stakeholder_expectations]

    insert_statement = MySQLStatementBuilder(db_connection)
    insert_statement \
        .insert(table=CVS_VCS_TABLE_ROWS_TABLE, columns=columns) \
        .set_values(values) \
        .execute(fetch_type=FetchType.FETCH_NONE)
    table_row_id = insert_statement.last_insert_id

    return get_vcs_table_row(db_connection, table_row_id, vcs_id, project_id, user_id)


def populate_vcs_table_row(db_result, vcs: models.VCS, project_id: int,
                           user_id: int) -> models.VCSTableRow:
    if db_result['iso_process']:
        iso_process = impl.get_iso_process(db_result['iso_process_id'])
        subprocesss = None
    else:
        iso_process = None
        subprocesss = impl.get_subprocess(db_result['subprocess_id'], project_id, user_id),

    return models.VCSTableRow(
        id=db_result['id'],
        stakeholder=db_result['stakeholder'],
        stakeholder_expectations=db_result['stakeholder_expectations'],
        iso_process=iso_process,
        subprocess=subprocesss,
        vcs=vcs,
    )


# ======================================================================================================================
# VCS Table
# ======================================================================================================================


def get_vcs_table(db_connection: PooledMySQLConnection, vcs_id: int, project_id: int, user_id: int) -> models.Table:
    impl.get_vcs(vcs_id, project_id, user_id)  # perfoming necessary controls

    # todo: 1) get all table rows
    # todo: 2) for each row, get all stakeholder needs
    # todo: 3) for each stakeholder need, get all value drivers

    table_rows = get_all_table_rows(db_connection, vcs_id, project_id, user_id)
    print(f'{table_rows = }')
    table = models.Table(table_rows=table_rows)
    print(f'{table = }')

    return table


def get_all_table_rows(db_connection: PooledMySQLConnection, vcs_id: int, project_id: int,
                       user_id: int) -> List[models.TableRow]:
    logger.debug(f'Fetching all table rows for VCS with id={vcs_id}.')

    where_statement = f'vcs_id = %s'
    where_values = [vcs_id]

    select_statement = MySQLStatementBuilder(db_connection)
    results = select_statement \
        .select(CVS_VCS_TABLE_ROWS_TABLE, CVS_VCS_TABLE_ROWS_COLUMNS) \
        .where(where_statement, where_values) \
        .order_by(['id'], Sort.ASCENDING) \
        .execute(fetch_type=FetchType.FETCH_ALL, dictionary=True)

    return [populate_table_row(result, result, project_id, user_id) for result in results]


def populate_table_row(db_connection: PooledMySQLConnection, db_result, project_id: int,
                       user_id: int) -> models.TableRow:
    if db_result['iso_process_id']:
        iso_process = impl.get_iso_process(db_result['iso_process_id'])
        subprocesss = None
    else:
        iso_process = None
        subprocesss = impl.get_subprocess(db_result['subprocess_id'], project_id, user_id),

    return models.TableRow(
        id=db_result['id'],
        iso_process=iso_process,
        subprocess=subprocesss,
        stakeholder=db_result['stakeholder'],
        stakeholder_expectations=db_result['stakeholder_expectations'],
        stakeholder_needs=get_stakeholder_needs(db_connection, db_result['id'], project_id, user_id),
    )


def get_stakeholder_needs(db_connection: PooledMySQLConnection, table_row_id: int, project_id: int,
                          user_id: int) -> List[models.StakeholderNeed]:
    logger.debug(f'Fetching all stakeholder needs for VCS table row with id={table_row_id}.')

    where_statement = f'vcs_row_id = %s'
    where_values = [table_row_id]

    select_statement = MySQLStatementBuilder(db_connection)
    results = select_statement \
        .select(CVS_VCS_STAKEHOLDER_NEED_TABLE, CVS_VCS_STAKEHOLDER_NEED_COLUMNS) \
        .where(where_statement, where_values) \
        .order_by(['id'], Sort.ASCENDING) \
        .execute(fetch_type=FetchType.FETCH_ALL, dictionary=True)

    return [populate_stakeholder_need(db_connection, result, project_id, user_id) for result in results]


def populate_stakeholder_need(db_connection: PooledMySQLConnection, db_result, project_id: int,
                              user_id: int) -> models.StakeholderNeed:
    return models.StakeholderNeed(
        need=db_result['need'],
        rank_weight=db_result['rank_weight'],
        value_drivers=get_all_drivers_from_needs(db_connection, db_result['id'], project_id, user_id),
    )


def get_all_drivers_from_needs(db_connection: PooledMySQLConnection, stakeholder_need_id: int, project_id: int,
                               user_id: int) -> List[models.ValueDriver]:
    logger.debug(f'Fetching all value drivers for stakeholder need with id={stakeholder_need_id}.')

    where_statement = f'stakeholder_need_id = %s'
    where_values = [stakeholder_need_id]

    select_statement = MySQLStatementBuilder(db_connection)
    results = select_statement \
        .select(CVS_VCS_NEEDS_DRIVERS_MAP_TABLE, ['value_driver_id']) \
        .where(where_statement, where_values) \
        .order_by(['id'], Sort.ASCENDING) \
        .execute(fetch_type=FetchType.FETCH_ALL, dictionary=True)

    value_drivers = []
    for result in results:
        value_driver = get_value_driver(db_connection, result['id'], project_id, user_id)
        value_drivers.append(models.ValueDriver(id=value_driver.id, name=value_driver.name))

    return value_drivers


def create_vcs_table():
    pass


def edit_vcs_table():
    pass
    # todo: 1) validate input
    # todo: 2) delete all existing tables rows
    # todo: 3) create new table rows

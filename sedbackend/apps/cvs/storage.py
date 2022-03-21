from mysql.connector.pooling import PooledMySQLConnection
from fastapi.logger import logger
from typing import List

import sedbackend.apps.core.authentication.exceptions as auth_exceptions
from sedbackend.apps.core.users.storage import db_get_user_safe_with_id
import sedbackend.apps.cvs.implementation as impl
import sedbackend.apps.cvs.models as models
import sedbackend.apps.cvs.exceptions as cvs_exceptions

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
CVS_VCS_SUBPROCESS_COLUMNS = ['id', 'name', 'parent_process_id', 'project_id', 'order_index']

CVS_VCS_TABLE_ROWS_TABLE = 'cvs_vcs_table_rows'
CVS_VCS_TABLE_ROWS_COLUMNS = ['id', 'row_index', 'vcs_id', 'iso_process_id', 'subprocess_id', 'stakeholder',
                              'stakeholder_expectations']

CVS_VCS_STAKEHOLDER_NEED_TABLE = 'cvs_vcs_stakeholder_needs'
CVS_VCS_STAKEHOLDER_NEED_COLUMNS = ['id', 'table_row_id', 'need', 'rank_weight']

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
        .order_by(['id'], Sort.ASCENDING) \
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
        raise cvs_exceptions.ValueDriverNotFoundException(value_driver_id=value_driver_id)

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
        raise cvs_exceptions.ValueDriverNotFoundException(value_driver_id=value_driver_id)

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
        raise cvs_exceptions.SubprocessNotFoundException(subprocess_id)

    if result['project_id'] != project_id:
        raise auth_exceptions.UnauthorizedOperationException

    return populate_subprocess(db_connection, result, project_id, user_id)


def create_subprocess(db_connection: PooledMySQLConnection, subprocess_post: models.VCSSubprocessPost,
                      project_id: int, user_id: int) -> models.VCSSubprocess:
    logger.debug(f'Creating a subprocesses in project with id={project_id}.')

    # performing necessary checks
    get_cvs_project(db_connection, project_id, user_id)
    get_iso_process(subprocess_post.parent_process_id)

    columns = ['name', 'parent_process_id', 'project_id', 'order_index']
    values = [subprocess_post.name, subprocess_post.parent_process_id, project_id, subprocess_post.order_index]

    insert_statement = MySQLStatementBuilder(db_connection)
    insert_statement \
        .insert(table=CVS_VCS_SUBPROCESS_TABLE, columns=columns) \
        .set_values(values) \
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

    # performing necessary checks
    get_cvs_project(db_connection, project_id, user_id)
    get_iso_process(new_subprocess.parent_process_id)

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
        raise cvs_exceptions.SubprocessFailedToUpdateException(subprocess_id)

    return get_subprocess(db_connection, subprocess_id, project_id, user_id)


def delete_subprocess(db_connection: PooledMySQLConnection, subprocess_id: int, project_id: int, user_id: int) -> bool:
    logger.debug(f'Deleting subprocesses with id={subprocess_id}.')

    get_cvs_project(db_connection, project_id, user_id)  # performing necessary checks

    select_statement = MySQLStatementBuilder(db_connection)
    result = select_statement \
        .select(CVS_VCS_SUBPROCESS_TABLE, CVS_VCS_SUBPROCESS_COLUMNS) \
        .where('id = %s', [subprocess_id]) \
        .execute(fetch_type=FetchType.FETCH_ONE, dictionary=True)

    if result is None:
        raise cvs_exceptions.SubprocessNotFoundException(subprocess_id)

    if result['project_id'] != project_id:
        raise auth_exceptions.UnauthorizedOperationException

    delete_statement = MySQLStatementBuilder(db_connection)
    _, rows = delete_statement.delete(CVS_VCS_SUBPROCESS_TABLE) \
        .where('id = %s', [subprocess_id]) \
        .execute(return_affected_rows=True)

    if rows == 0:
        raise cvs_exceptions.SubprocessFailedDeletionException(subprocess_id)

    return True


def populate_subprocess(db_connection: PooledMySQLConnection, db_result, project_id: int,
                        user_id: int) -> models.VCSSubprocess:
    logger.debug(f'Populating model for subprocess with id={db_result["id"]}.')
    return models.VCSSubprocess(
        id=db_result['id'],
        name=db_result['name'],
        parent_process=get_iso_process(db_result['parent_process_id']),
        project=get_cvs_project(db_connection, project_id, user_id),
        order_index=db_result['order_index'],
    )


def update_subprocess_indices(db_connection: PooledMySQLConnection, subprocess_ids: List[int], order_indices: List[int],
                              project_id: int, user_id: int) -> bool:
    logger.debug(f'Updating indices for subprocesses with ids={subprocess_ids}.')

    # Performs necessary checks
    subprocesses = [get_subprocess(db_connection, _id, project_id, user_id) for _id in subprocess_ids]

    for subprocess, index in zip(subprocesses, order_indices):
        if index == subprocess.order_index:
            continue  # skipping since otherwise affected rows will be 0

        update_statement = MySQLStatementBuilder(db_connection)
        update_statement.update(
            table=CVS_VCS_SUBPROCESS_TABLE,
            set_statement='order_index = %s',
            values=[index],
        )
        update_statement.where('id = %s', [subprocess.id])
        _, rows = update_statement.execute(return_affected_rows=True)

        if rows == 0:
            raise cvs_exceptions.SubprocessFailedToUpdateException(subprocess_id=subprocess.id)

    return True


# ======================================================================================================================
# VCS Table
# ======================================================================================================================

def get_vcs_table(db_connection: PooledMySQLConnection, vcs_id: int, project_id: int, user_id: int) -> models.TableGet:
    logger.debug(f'Fetching all table for VCS with id={vcs_id}.')
    table_rows = get_all_table_rows(db_connection, vcs_id, project_id, user_id)
    return models.TableGet(table_rows=table_rows)


def get_all_table_rows(db_connection: PooledMySQLConnection, vcs_id: int, project_id: int,
                       user_id: int) -> List[models.TableRowGet]:
    logger.debug(f'Fetching all table rows for VCS with id={vcs_id}.')

    where_statement = f'vcs_id = %s'
    where_values = [vcs_id]

    select_statement = MySQLStatementBuilder(db_connection)
    results = select_statement \
        .select(CVS_VCS_TABLE_ROWS_TABLE, CVS_VCS_TABLE_ROWS_COLUMNS) \
        .where(where_statement, where_values) \
        .order_by(['id'], Sort.ASCENDING) \
        .execute(fetch_type=FetchType.FETCH_ALL, dictionary=True)

    return [populate_table_row(db_connection, result, project_id, user_id) for result in results]


def populate_table_row(db_connection: PooledMySQLConnection, db_result, project_id: int,
                       user_id: int) -> models.TableRowGet:
    logger.debug(f'Populating model for table row with id={db_result["id"]}.')

    iso_process, subprocesss = None, None
    if db_result['iso_process_id'] is not None:
        iso_process = get_iso_process(db_result['iso_process_id'])
    elif db_result['subprocess_id'] is not None:
        try:
            subprocesss = get_subprocess(db_connection, db_result['subprocess_id'], project_id, user_id)
        except cvs_exceptions.SubprocessNotFoundException:
            # If a subprocess is deleted but used in a table, the subprocess wont be found and thus this exception
            pass

    return models.TableRowGet(
        id=db_result['id'],
        row_index=db_result['row_index'],
        iso_process=iso_process,
        subprocess=subprocesss,
        stakeholder=db_result['stakeholder'],
        stakeholder_expectations=db_result['stakeholder_expectations'],
        stakeholder_needs=get_stakeholder_needs(db_connection, db_result['id'], project_id, user_id),
    )


def get_stakeholder_needs(db_connection: PooledMySQLConnection, table_row_id: int, project_id: int,
                          user_id: int) -> List[models.StakeholderNeedGet]:
    logger.debug(f'Fetching all stakeholder needs for VCS table row with id={table_row_id}.')

    where_statement = f'table_row_id = %s'
    where_values = [table_row_id]

    results = MySQLStatementBuilder(db_connection) \
        .select(CVS_VCS_STAKEHOLDER_NEED_TABLE, CVS_VCS_STAKEHOLDER_NEED_COLUMNS) \
        .where(where_statement, where_values) \
        .order_by(['id'], Sort.ASCENDING) \
        .execute(fetch_type=FetchType.FETCH_ALL, dictionary=True)

    return [populate_stakeholder_need(db_connection, result, project_id, user_id) for result in results]


def populate_stakeholder_need(db_connection: PooledMySQLConnection, db_result, project_id: int,
                              user_id: int) -> models.StakeholderNeedGet:
    logger.debug(f'Populating model for stakeholder need with id={db_result["id"]}.')
    return models.StakeholderNeedGet(
        id=db_result['id'],
        need=db_result['need'],
        rank_weight=db_result['rank_weight'],
        value_drivers=get_drivers_from_needs(db_connection, db_result['id'], project_id, user_id),
    )


def get_drivers_from_needs(db_connection: PooledMySQLConnection, stakeholder_need_id: int, project_id: int,
                           user_id: int) -> List[models.ValueDriverGet]:
    logger.debug(f'Fetching all value drivers for stakeholder need with id={stakeholder_need_id}.')

    where_statement = f'stakeholder_need_id = %s'
    where_values = [stakeholder_need_id]

    results = MySQLStatementBuilder(db_connection) \
        .select(CVS_VCS_NEEDS_DRIVERS_MAP_TABLE, ['value_driver_id']) \
        .where(where_statement, where_values) \
        .order_by(['value_driver_id'], Sort.ASCENDING) \
        .execute(fetch_type=FetchType.FETCH_ALL, dictionary=True)

    value_drivers = []
    for result in results:
        value_driver = get_value_driver(db_connection, result['value_driver_id'], project_id, user_id)
        value_drivers.append(models.ValueDriverGet(id=value_driver.id, name=value_driver.name))

    return value_drivers


def create_vcs_table(db_connection: PooledMySQLConnection, new_table: models.TablePost, vcs_id: int, project_id: int,
                     user_id: int) -> bool:
    logger.debug(f'Creating table for VCS with id={vcs_id}.')

    # Getting ids of any existing rows
    results = MySQLStatementBuilder(db_connection) \
        .select(CVS_VCS_TABLE_ROWS_TABLE, ['id']) \
        .where(f'vcs_id = %s', [vcs_id]) \
        .order_by(['id'], Sort.ASCENDING) \
        .execute(fetch_type=FetchType.FETCH_ALL, dictionary=True)

    # Deleting any existing rows
    for result in results:
        delete_statement = MySQLStatementBuilder(db_connection)
        _, rows = delete_statement.delete(CVS_VCS_TABLE_ROWS_TABLE) \
            .where('id = %s', [result['id']]) \
            .execute(return_affected_rows=True)

        if rows == 0:
            raise cvs_exceptions.VCSTableRowFailedDeletionException(result['id'])

    # Creating new rows
    for i, table_row in enumerate(new_table.table_rows):

        # Checking processes
        if (table_row.iso_process_id is None) and (table_row.subprocess_id is None):
            # no process provided
            iso_process_id = None
            subprocess_id = None

        elif (table_row.iso_process_id is not None) and (table_row.subprocess_id is not None):
            # two processes provided
            raise cvs_exceptions.VCSTableProcessAmbiguity(table_row_id=i)

        elif table_row.iso_process_id is not None:
            # iso process provided
            iso_process_id = impl.get_iso_process(table_row.iso_process_id).id
            subprocess_id = None

        else:
            # subprocess provided
            iso_process_id = None
            subprocess_id = impl.get_subprocess(table_row.subprocess_id, project_id, user_id).id

        # Further checking provided data
        stakeholder = table_row.stakeholder if table_row.stakeholder is not None else ''
        stakeholder_exp = table_row.stakeholder_expectations if table_row.stakeholder_expectations is not None else ''

        columns = ['vcs_id', 'row_index', 'iso_process_id', 'subprocess_id', 'stakeholder', 'stakeholder_expectations']
        values = [vcs_id, table_row.row_index, iso_process_id, subprocess_id, stakeholder, stakeholder_exp]

        insert_statement = MySQLStatementBuilder(db_connection)
        insert_statement \
            .insert(table=CVS_VCS_TABLE_ROWS_TABLE, columns=columns) \
            .set_values(values) \
            .execute(fetch_type=FetchType.FETCH_NONE)
        table_row_id = insert_statement.last_insert_id

        for stakeholder_need in table_row.stakeholder_needs:

            need = stakeholder_need.need if stakeholder_need is not None else ''
            rank_weight = stakeholder_need.rank_weight if stakeholder_need.rank_weight is not None else 0

            insert_statement = MySQLStatementBuilder(db_connection)
            insert_statement \
                .insert(table=CVS_VCS_STAKEHOLDER_NEED_TABLE, columns=['table_row_id', 'need', 'rank_weight']) \
                .set_values([table_row_id, need, rank_weight]) \
                .execute(fetch_type=FetchType.FETCH_NONE)
            stakeholder_need_id = insert_statement.last_insert_id

            for value_driver_id in stakeholder_need.value_driver_ids:
                get_value_driver(db_connection, value_driver_id, project_id, user_id)  # perfoms necessary controls

                insert_statement = MySQLStatementBuilder(db_connection)
                insert_statement \
                    .insert(table=CVS_VCS_NEEDS_DRIVERS_MAP_TABLE, columns=['stakeholder_need_id', 'value_driver_id']) \
                    .set_values([stakeholder_need_id, value_driver_id]) \
                    .execute(fetch_type=FetchType.FETCH_NONE)

    return True

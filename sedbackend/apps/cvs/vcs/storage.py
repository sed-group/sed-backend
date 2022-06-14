from multiprocessing import Pool
from pyexpat import model
from sys import stdout
from typing import List

from fastapi.logger import logger
from mysql.connector.pooling import PooledMySQLConnection

from sedbackend.apps.core.authentication import exceptions as auth_exceptions
from sedbackend.apps.cvs import project
from sedbackend.apps.cvs import vcs
from sedbackend.apps.cvs.project.storage import get_cvs_project
from sedbackend.apps.cvs.life_cycle.storage import create_node, update_node
from sedbackend.apps.cvs.life_cycle.models import NodePost
from sedbackend.apps.cvs.vcs import models, exceptions, implementation
from sedbackend.libs import mysqlutils
from sedbackend.libs.datastructures.pagination import ListChunk
from sedbackend.libs.mysqlutils import MySQLStatementBuilder, Sort, FetchType

CVS_VCS_TABLE = 'cvs_vcss'
CVS_VCS_COLUMNS = ['id', 'name', 'description', 'datetime_created', 'year_from', 'year_to', 'project']

CVS_VALUE_DIMENSION_TABLE = 'cvs_value_dimensions'
CVS_VALUE_DIMENSION_COLUMNS = ['id', 'name', 'priority', 'vcs_row']

CVS_VALUE_DRIVER_TABLE = 'cvs_value_drivers'
CVS_VALUE_DRIVER_COLUMNS = ['id', 'name', 'unit', 'value_dimension']

CVS_VCS_ROW_DRIVERS_TABLE = 'cvs_rowDrivers'
CVS_VCS_ROW_DRIVERS_COLUMNS = ['vcs_row', 'value_driver']

CVS_ISO_PROCESS_TABLE = 'cvs_iso_processes'
CVS_ISO_PROCESS_COLUMNS = ['id', 'name', 'category']

CVS_VCS_SUBPROCESS_TABLE = 'cvs_subprocesses'
CVS_VCS_SUBPROCESS_COLUMNS = ['id', 'name', 'order_index', 'iso_process']

CVS_VCS_ROWS_TABLE = 'cvs_vcs_rows'
CVS_VCS_ROWS_COLUMNS = ['id', 'index', 'stakeholder', 'stakeholder_needs',
                              'stakeholder_expectations', 'iso_process', 'subprocess', 'vcs']
CVS_VCS_STAKEHOLDER_NEED_TABLE = 'cvs_vcs_stakeholder_needs'
CVS_VCS_STAKEHOLDER_NEED_COLUMNS = ['id', 'table_row_id', 'need', 'rank_weight']

CVS_VCS_NEEDS_DRIVERS_MAP_TABLE = 'cvs_vcs_needs_divers_map'
CVS_VCS_NEEDS_DRIVERS_MAP_COLUMNS = ['id', 'stakeholder_need_id', 'value_driver_id']


# ======================================================================================================================
# VCS (Value Creation Strategy)
# ======================================================================================================================


def get_all_vcs(db_connection: PooledMySQLConnection, project_id: int, user_id: int) -> ListChunk[
    models.VCS]:
    logger.debug(f'Fetching all VCSs for project with id={project_id}.')

    get_cvs_project(db_connection, project_id, user_id)  # perform checks: project and user

    where_statement = f'project = %s'
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

    where_statement = f'project = %s'
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

    get_cvs_project(db_connection, project_id, user_id)  # perform necessary checks for project and user

    select_statement = MySQLStatementBuilder(db_connection)
    result = select_statement \
        .select(CVS_VCS_TABLE, CVS_VCS_COLUMNS) \
        .where('id = %s', [vcs_id]) \
        .execute(fetch_type=FetchType.FETCH_ONE, dictionary=True)

    if result is None:
        raise exceptions.VCSNotFoundException

    if result['project'] != project_id:
        raise auth_exceptions.UnauthorizedOperationException

    return populate_vcs(db_connection, result, project_id, user_id)


def create_vcs(db_connection: PooledMySQLConnection, vcs_post: models.VCSPost, project_id: int,
               user_id: int) -> models.VCS:
    logger.debug(f'Creating a VCS in project with id={project_id}.')

    get_cvs_project(db_connection, project_id, user_id)  # performs checks for existing project and correct user

    insert_statement = MySQLStatementBuilder(db_connection)
    insert_statement \
        .insert(table=CVS_VCS_TABLE, columns=['name', 'description', 'year_from', 'year_to', 'project']) \
        .set_values([vcs_post.name, vcs_post.description, vcs_post.year_from, vcs_post.year_to, project_id]) \
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
        raise exceptions.VCSFailedToUpdateException

    return get_vcs(db_connection, vcs_id, project_id, user_id)


def delete_vcs(db_connection: PooledMySQLConnection, vcs_id: int, project_id: int, user_id: int) -> bool:
    logger.debug(f'Deleting VCS with id={vcs_id}.')

    select_statement = MySQLStatementBuilder(db_connection)

    result = select_statement \
        .select(CVS_VCS_TABLE, CVS_VCS_COLUMNS) \
        .where('id = %s', [vcs_id]) \
        .execute(fetch_type=FetchType.FETCH_ONE, dictionary=True)

    if result is None:
        raise exceptions.VCSNotFoundException

    get_cvs_project(db_connection, project_id, user_id)  # performs checks for existing project and correct user

    delete_statement = MySQLStatementBuilder(db_connection)
    _, rows = delete_statement.delete(CVS_VCS_TABLE) \
        .where('id = %s', [vcs_id]) \
        .execute(return_affected_rows=True)

    if rows == 0:
        raise exceptions.VCSFailedDeletionException

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
# VCS Value Dimensions
# ======================================================================================================================
def get_value_dimension(db_connection: PooledMySQLConnection, value_dimension_id: int, vcs_row: int) -> models.ValueDimension:
    logger.debug(f'Fetching a single value dimension with id: {value_dimension_id}')

    select_statement = MySQLStatementBuilder(db_connection)
    res = select_statement \
        .select(CVS_VALUE_DIMENSION_TABLE, CVS_VALUE_DIMENSION_COLUMNS)\
        .where(f'id = %s', [value_dimension_id])\
        .execute(FetchType.FETCH_ONE, dictionary=True)
    
    if res is None:
        raise exceptions.ValueDimensionNotFoundException
    
    if res['vcs_row'] != vcs_row:
        raise exceptions.VCSRowNotCorrectException
    
    return populate_value_dimension(res, res['vcs_row'])

def get_all_row_value_dimensions(db_connection: PooledMySQLConnection, vcs_row: int) -> List[models.ValueDimension]:
    logger.debug(f'Fetching all value dimensions for a single vcs row')

    select_statement = MySQLStatementBuilder(db_connection)
    res = select_statement \
        .select(CVS_VALUE_DIMENSION_TABLE, CVS_VALUE_DIMENSION_COLUMNS)\
        .where(f'vcs_row = %s', [vcs_row])\
        .execute(FetchType.FETCH_ALL, dictionary=True)

    return [populate_value_dimension(result, vcs_row) for result in res]


def create_value_dimension(db_connection: PooledMySQLConnection, value_dimension_post: models.ValueDimensionPost, vcs_row: int) -> models.ValueDimension:
    logger.debug(f'Inserting a new value dimension')

    insert_statement = MySQLStatementBuilder(db_connection)
    res = insert_statement \
        .insert(CVS_VALUE_DIMENSION_TABLE, ['name', 'priority', 'vcs_row'])\
        .set_values([value_dimension_post.name, value_dimension_post.priority, vcs_row]) \
        .execute(fetch_type=FetchType.FETCH_ONE, dictionary=True)
    
    return get_value_dimension(db_connection, insert_statement.last_insert_id, vcs_row)

def edit_value_dimension(db_connection: PooledMySQLConnection, dimension_id: int, updated_dimension: models.ValueDimensionPost, vcs_row: int) -> models.ValueDimension:
    logger.debug(f'Editing value dimension with id={dimension_id}')

    update_statement = MySQLStatementBuilder(db_connection)
    res = update_statement \
        .update(CVS_VALUE_DIMENSION_TABLE, 'name = %s, priority = %s, vcs_row = %s', [updated_dimension.name, updated_dimension.priority, vcs_row])\
        .where(f'id = %s', [dimension_id])\
        .execute(fetch_type=FetchType.FETCH_ONE, dictionary=True)
    
    return get_value_dimension(db_connection, dimension_id, vcs_row)

def populate_value_dimension(db_result, vcs_row: int) -> models.ValueDimension:
    return models.ValueDimension(
        id=db_result['id'],
        name=db_result['name'],
        priority=db_result['priority'],
        vcs_row=vcs_row
    )
# ======================================================================================================================
# VCS Value driver
# ======================================================================================================================


def get_all_value_driver(db_connection: PooledMySQLConnection, project_id: int) -> List[models.ValueDriver]:
    logger.debug(f'Fetching all value drivers for project with id={project_id}.')
    #Fetches only the value drivers that has a connection with a vcs row.

    query = f'SELECT cvs_value_drivers.id, cvs_value_drivers.name, unit, value_dimension FROM cvs_value_drivers \
            INNER JOIN cvs_rowDrivers ON cvs_value_drivers.id = value_driver \
            INNER JOIN cvs_vcs_rows ON vcs_row = cvs_vcs_rows.id \
            INNER JOIN cvs_vcss ON vcs = cvs_vcss.id \
            WHERE project = %s'
    with db_connection.cursor(prepared=True) as cursor:
        cursor.execute(query, [project_id])
        res = cursor.fetchall()

        if res == None:
            raise exceptions.ValueDriverNotFoundException
        
        res = [dict(zip(cursor.column_names, row)) for row in res]
    
    return [populate_value_driver(result) for result in res]


def get_value_driver(db_connection: PooledMySQLConnection, value_driver_id: int) -> models.ValueDriver:
    logger.debug(f'Fetching value driver with id={value_driver_id}.')

    where_statement = f'id = %s'
    where_values = [value_driver_id]

    select_statement = MySQLStatementBuilder(db_connection)
    result = select_statement \
        .select(CVS_VALUE_DRIVER_TABLE, CVS_VALUE_DRIVER_COLUMNS) \
        .where(where_statement, where_values) \
        .execute(fetch_type=FetchType.FETCH_ONE, dictionary=True)

    if result is None:
        raise exceptions.ValueDriverNotFoundException(value_driver_id=value_driver_id)

    return populate_value_driver(result)


def create_value_driver(db_connection: PooledMySQLConnection, value_driver_post: models.ValueDriverPost) -> models.ValueDriver:
    logger.debug(f'Creating a value driver')

    insert_statement = MySQLStatementBuilder(db_connection)
    insert_statement \
        .insert(table=CVS_VALUE_DRIVER_TABLE, columns=['name', 'unit', 'value_dimension']) \
        .set_values([value_driver_post.name, value_driver_post.unit, value_driver_post.value_dimension]) \
        .execute(fetch_type=FetchType.FETCH_NONE)
    value_driver_id = insert_statement.last_insert_id

    return get_value_driver(db_connection, value_driver_id)


def edit_value_driver(db_connection: PooledMySQLConnection, value_driver_id: int, 
            new_value_driver: models.ValueDriverPost) -> models.ValueDriver:
    logger.debug(f'Editing value driver with id={value_driver_id}.')

    #old_value_driver = get_value_driver(db_connection, value_driver_id, project_id, user_id)
    #if old_value_driver.name == new_value_driver.name:  # No change
    #    return old_value_driver

    # Updating
    update_statement = MySQLStatementBuilder(db_connection)
    update_statement.update(
        table=CVS_VALUE_DRIVER_TABLE,
        set_statement='name = %s, unit = %s, value_dimension = %s',
        values=[new_value_driver.name, new_value_driver.unit, new_value_driver.value_dimension],
    )
    update_statement.where('id = %s', [value_driver_id])
    _, rows = update_statement.execute(return_affected_rows=True)

    if rows == 0:
        raise exceptions.ValueDriverFailedToUpdateException

    return get_value_driver(db_connection, value_driver_id)


def delete_value_driver(db_connection: PooledMySQLConnection, value_driver_id: int,
                        user_id: int) -> bool:
    logger.debug(f'Deleting value driver with id={value_driver_id}.')

    delete_statement = MySQLStatementBuilder(db_connection)
    _, rows = delete_statement.delete(CVS_VALUE_DRIVER_TABLE) \
        .where('id = %s', [value_driver_id]) \
        .execute(return_affected_rows=True)

    if rows == 0:
        raise exceptions.ValueDriverNotFoundException(value_driver_id=value_driver_id)

    return True


def populate_value_driver(db_result) -> models.ValueDriver:
    return models.ValueDriver(
        id=db_result['id'],
        name=db_result['name'],
        unit=db_result['unit'],
        value_dimension=db_result['value_dimension']
    )




# ======================================================================================================================
# VCS ISO Processes
# ======================================================================================================================


def get_all_iso_process(db_connection: PooledMySQLConnection) -> List[models.VCSISOProcess]:
    logger.debug(f'Fetching all ISO processes.')

    select_statement = MySQLStatementBuilder(db_connection)
    results = select_statement \
        .select(CVS_ISO_PROCESS_TABLE, CVS_ISO_PROCESS_COLUMNS) \
        .execute(FetchType.FETCH_ALL, dictionary=True)
    
    iso_processes = []

    for res in results:
        iso_processes.append(populate_iso_process(res))
    
    return iso_processes


def get_iso_process(iso_process_id: int, db_connection) -> models.VCSISOProcess:
    logger.debug(f'Fetching ISO process with id={iso_process_id}.')
    
    select_statement = MySQLStatementBuilder(db_connection)
    result = select_statement \
        .select(CVS_ISO_PROCESS_TABLE, CVS_ISO_PROCESS_COLUMNS) \
        .where(f'id = %s', [iso_process_id]) \
        .execute(FetchType.FETCH_ONE, dictionary=True)
    
    if result == None:
        raise exceptions.ISOProcessNotFoundException

    return populate_iso_process(result)
    

def populate_iso_process(db_result):
    return models.VCSISOProcess(
        id=db_result['id'],
        name=db_result['name'],
        category=db_result['category']
    )

# ======================================================================================================================
# VCS Subprocesses
# ======================================================================================================================

def get_all_subprocess(db_connection: PooledMySQLConnection, vcs_id: int,
                       user_id: int) -> List[models.VCSSubprocess]:
    logger.debug(f'Fetching all subprocesses for vcs with id={vcs_id}.')

    
    query = f'SELECT cvs_subprocesses.id, cvs_subprocesses.name, order_index, \
        iso_process, cvs_iso_processes.name as iso_process_name, category \
        FROM cvs_subprocesses INNER JOIN cvs_iso_processes ON iso_process = cvs_iso_processes.id\
        INNER JOIN cvs_vcs_rows ON subprocess = cvs_subprocesses.id'
    with db_connection.cursor(prepared=True) as cursor:
        cursor.execute(query, [vcs_id])
        last_insert_id = cursor.lastrowid
        res = cursor.fetchall()
        
        if res == None:
            raise exceptions.SubprocessNotFoundException
        
        res = [dict(zip(cursor.column_names, row)) for row in res]

        
    subprocess_list = [populate_subprocess(result) for result in res]

    return subprocess_list


def get_subprocess(db_connection: PooledMySQLConnection, subprocess_id: int) -> models.VCSSubprocess:
    logger.debug(f'Fetching subprocess with id={subprocess_id}.')

    query = f'SELECT cvs_subprocesses.id, cvs_subprocesses.name, order_index, \
        iso_process, cvs_iso_processes.name as iso_process_name, category \
        FROM cvs_subprocesses INNER JOIN cvs_iso_processes ON iso_process = cvs_iso_processes.id\
        WHERE cvs_subprocesses.id = %s'
    with db_connection.cursor(prepared=True) as cursor:
        cursor.execute(query, [subprocess_id])
        last_insert_id = cursor.lastrowid
        res = cursor.fetchone()
        res = dict(zip(cursor.column_names, res))

    if res is None:
        raise exceptions.SubprocessNotFoundException(subprocess_id)

    return populate_subprocess(res)


def create_subprocess(db_connection: PooledMySQLConnection, subprocess_post: models.VCSSubprocessPost) -> models.VCSSubprocess:
    logger.debug(f'Creating a subprocesses.')

    columns = ['name', 'order_index', 'iso_process']
    values = [subprocess_post.name, subprocess_post.order_index, subprocess_post.parent_process_id]

    insert_statement = MySQLStatementBuilder(db_connection)
    insert_statement \
        .insert(table=CVS_VCS_SUBPROCESS_TABLE, columns=columns) \
        .set_values(values) \
        .execute(fetch_type=FetchType.FETCH_NONE)
    subprocess_id = insert_statement.last_insert_id

    return get_subprocess(db_connection, subprocess_id)


def edit_subprocess(db_connection: PooledMySQLConnection, subprocess_id: int, project_id: int, user_id: int,
                    new_subprocess: models.VCSSubprocessPost) -> models.VCSSubprocess:
    logger.debug(f'Editing subprocesses with id={subprocess_id}.')

    old_subprocess = get_subprocess(db_connection, subprocess_id)
    o = (old_subprocess.name, old_subprocess.parent_process.id)
    n = (new_subprocess.name, new_subprocess.parent_process_id)
    if o == n:  # No change
        return old_subprocess

    # performing necessary checks
    get_cvs_project(db_connection, project_id, user_id)

    # Updating
    update_statement = MySQLStatementBuilder(db_connection)
    update_statement.update(
        table=CVS_VCS_SUBPROCESS_TABLE,
        set_statement='name = %s, iso_process = %s',
        values=[new_subprocess.name, new_subprocess.parent_process_id],
    )
    update_statement.where('id = %s', [subprocess_id])
    _, rows = update_statement.execute(return_affected_rows=True)

    if rows == 0:
        raise exceptions.SubprocessFailedToUpdateException(subprocess_id)

    return get_subprocess(db_connection, subprocess_id)


def delete_subprocess(db_connection: PooledMySQLConnection, subprocess_id: int) -> bool:
    logger.debug(f'Deleting subprocesses with id={subprocess_id}.')

   # get_cvs_project(db_connection, project_id, user_id)  # performing necessary checks

    select_statement = MySQLStatementBuilder(db_connection)
    result = select_statement \
        .select(CVS_VCS_SUBPROCESS_TABLE, CVS_VCS_SUBPROCESS_COLUMNS) \
        .where('id = %s', [subprocess_id]) \
        .execute(fetch_type=FetchType.FETCH_ONE, dictionary=True)

    if result is None:
        raise exceptions.SubprocessNotFoundException(subprocess_id)

 #   if result['project_id'] != project_id:
 #       raise auth_exceptions.UnauthorizedOperationException

    delete_statement = MySQLStatementBuilder(db_connection)
    _, rows = delete_statement.delete(CVS_VCS_SUBPROCESS_TABLE) \
        .where('id = %s', [subprocess_id]) \
        .execute(return_affected_rows=True)
    
    #TODO after deleting subprocesses - make sure to update the order indices. 
    if rows == 0:
        raise exceptions.SubprocessFailedDeletionException(subprocess_id)

    return True


def populate_subprocess(db_result) -> models.VCSSubprocess:
    logger.debug(f'Populating model for subprocess with id={db_result["id"]}.')
  #  print("in populate: " + db_result['iso_process'])
    return models.VCSSubprocess(
        id=db_result['id'],
        name=db_result['name'],
        order_index=db_result['order_index'],
        vcs_id=db_result['vcs'],
        parent_process=models.VCSISOProcess(
            id=db_result['iso_process'],
            name=db_result['iso_process_name'],
            category=db_result['category']
            )
    )

def update_subprocess_indices(db_connection: PooledMySQLConnection, subprocess_ids: List[int], order_indices: List[int],
                              project_id: int, user_id: int) -> bool:
    logger.debug(f'Updating indices for subprocesses with ids={subprocess_ids}.')

    # Performs necessary checks
    subprocesses = [get_subprocess(db_connection, _id) for _id in subprocess_ids]

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
            raise exceptions.SubprocessFailedToUpdateException(subprocess_id=subprocess.id)

    return True


# ======================================================================================================================
# VCS Rows
# ======================================================================================================================

def get_vcs_table(db_connection: PooledMySQLConnection, vcs_id: int,  user_id: int) -> List[models.VcsRow]:
    logger.debug(f'Fetching all table for VCS with id={vcs_id}.')
#    table_rows = get_all_table_rows(db_connection, vcs_id, user_id)

    select_statement = MySQLStatementBuilder(db_connection)
    results = select_statement \
        .select(CVS_VCS_ROWS_TABLE, CVS_VCS_ROWS_COLUMNS) \
        .where(f'vcs = %s', [vcs_id]) \
        .order_by(['index'], Sort.ASCENDING) \
        .execute(fetch_type=FetchType.FETCH_ALL, dictionary=True)
    
    dimension_query = f'SELECT cvs_value_dimensions.id, cvs_value_dimensions.name, priority, vcs_row\
        FROM cvs_value_dimensions INNER JOIN cvs_vcs_rows ON vcs_row = cvs_vcs_rows.id\
        WHERE vcs = %s'
    with db_connection.cursor(prepared=True) as cursor:
        cursor.execute(dimension_query, [vcs_id])
        dimensions = cursor.fetchall()
        dimensions = [dict(zip(cursor.column_names, row)) for row in dimensions]
        
    dimension_dict = dict({})
    for res in dimensions:
        if dimension_dict.get(res['vcs_row']) is None:
            dimension_dict[res['vcs_row']] = [populate_value_dimension(res, res['vcs_row'])]
        else:
            dimension_dict.get(res['vcs_row']).append(populate_value_dimension(res, res['vcs_row']))

    query = f'SELECT vcs_row, cvs_value_drivers.id, `name`, unit, value_dimension \
            FROM cvs_vcs_rows INNER JOIN cvs_rowDrivers ON cvs_vcs_rows.id = vcs_row \
            INNER JOIN cvs_value_drivers ON value_driver = cvs_value_drivers.id \
            WHERE vcs = %s'
    with db_connection.cursor(prepared=True) as cursor:
        cursor.execute(query, [vcs_id])
        drivers = cursor.fetchall()
        drivers = [dict(zip(cursor.column_names, row)) for row in drivers]
    
    
    #TODO Fix so that value dimensions work with the vcs_rows

    driver_dict = dict({})
    for res in drivers:
        if driver_dict.get(res['vcs_row']) is None:
            driver_dict[res['vcs_row']] = [populate_value_driver(res)]
        else:
            driver_dict.get(res['vcs_row']).append(populate_value_driver(res))

    return [populate_vcs_row(db_connection, result, driver_dict, dimension_dict) for result in results]
    
def get_vcs_row(db_connection: PooledMySQLConnection, vcs_row_id: int) -> models.VcsRow:
    logger.debug(f'Fetching a single vcs row with id: {vcs_row_id}')

    select_statement = MySQLStatementBuilder(db_connection)
    result = select_statement \
        .select(CVS_VCS_ROWS_TABLE, CVS_VCS_ROWS_COLUMNS)\
        .where(f'id = %s', [vcs_row_id])\
        .execute(fetch_type=FetchType.FETCH_ONE, dictionary=True)
    
    value_dimensions = dict({vcs_row_id: get_all_row_value_dimensions(db_connection, vcs_row_id)})


    query = f'SELECT vcs_row, cvs_value_drivers.id, `name`, unit, value_dimension \
            FROM cvs_value_drivers INNER JOIN cvs_rowDrivers ON cvs_vcs_rows.id = vcs_row \
            WHERE vcs_row = %s'
    with db_connection.cursor(prepared=True) as cursor:
        cursor.execute(query, [vcs_row_id])
        drivers = cursor.fetchall()
        drivers = [dict(zip(cursor.column_names, row)) for row in drivers]
    
    driver_dict = dict({})
    for res in drivers:
        if driver_dict.get(res['vcs_row']) is None:
            driver_dict[res['vcs_row']] = [populate_value_driver(res)]
        else:
            driver_dict.get(res['vcs_row']).append(populate_value_driver(res))

    return populate_vcs_row(db_connection, result, driver_dict, value_dimensions)
    

def populate_vcs_row(db_connection: PooledMySQLConnection, db_result, value_drivers: dict, value_dimensions: dict) -> models.VcsRow:
    logger.debug(f'Populating model for table row with id={db_result["id"]}.')

    iso_process, subprocesss = None, None
    if db_result['iso_process'] is not None:
        logger.debug(db_result['iso_process']) #There is a bug here when fetching an entire vcs table
        iso_process = get_iso_process(int(db_result['iso_process']), db_connection)  # Gets a iso process based on the id that we got from the DB result

    elif db_result['subprocess'] is not None:
        try:
            subprocesss = get_subprocess(db_connection, db_result['subprocess_id'])  # Runs a new query on subprocess table based on the id that is in the result of the db query. Why is that not referenced as a foreign key and run as a single query here?????
        except exceptions.SubprocessNotFoundException:
            # If a subprocess is deleted but used in a table, the subprocess wont be found and thus this exception
            pass

    return models.VcsRow(
        id=db_result['id'],
        index=db_result['index'],
        stakeholder=db_result['stakeholder'],
        stakeholder_expectations=db_result['stakeholder_expectations'],
        stakeholder_needs=db_result['stakeholder_needs'],
        iso_process=iso_process,
        subprocess=subprocesss,
        value_dimensions=value_dimensions.get(db_result['id']),
        value_drivers=value_drivers.get(db_result['id']),
        vcs_id=db_result['vcs']
    )




def create_vcs_table(db_connection: PooledMySQLConnection, new_vcs_rows: List[models.VcsRowPost], vcs_id: int) -> bool:
    logger.debug(f'Creating table for VCS with id={vcs_id}.')

    for row in new_vcs_rows:

        values = [row.index, row.stakeholder, row.stakeholder_expectations, row.stakeholder_needs, row.iso_process, row.subprocess, vcs_id]
        
        if row.iso_process is None and row.subprocess is None:
            raise exceptions.VCSTableProcessAmbiguity
        elif row.iso_process is not None and row.subprocess is not None:
            raise exceptions.VCSTableProcessAmbiguity
        
        insert_statement = MySQLStatementBuilder(db_connection)
        inserted_row = insert_statement \
            .insert(CVS_VCS_ROWS_TABLE, ['index', 'stakeholder', 'stakeholder_needs', 'stakeholder_expectations', 'iso_process', 'subprocess', 'vcs'])\
            .set_values(values)\
            .execute(fetch_type=FetchType.FETCH_ONE)

        logger.debug(inserted_row)
        if row.value_dimensions is not None: #Inserting into value dimension if value dimensions are specified
            #Insert into value dimension table
            for value_dimension in row.value_dimensions:
                create_value_dimension(db_connection, models.ValueDimensionPost(name=value_dimension.name, priority=value_dimension.priority), insert_statement.last_insert_id)

        if row.value_drivers is not None:
            for vd in row.value_drivers: #Insert all value drivers associated with this row into the rowDrivers table
                insert_driver = MySQLStatementBuilder(db_connection)
                insert_driver \
                    .insert(CVS_VCS_ROW_DRIVERS_TABLE, CVS_VCS_ROW_DRIVERS_COLUMNS)\
                    .set_values([insert_statement.last_insert_id, vd]) \
                    .execute(fetch_type=FetchType.FETCH_NONE)
        

    return True

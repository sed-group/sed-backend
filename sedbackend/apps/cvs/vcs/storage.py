from multiprocessing import Pool
from pyexpat import model
from sys import stdout
from typing import List

from fastapi.logger import logger
from mysql.connector.pooling import PooledMySQLConnection
from requests import delete
from mysql.connector import Error,errorcode



from sedbackend.apps.core.authentication import exceptions as auth_exceptions
from sedbackend.apps.cvs.project.storage import get_cvs_project
from sedbackend.apps.cvs.vcs import models, exceptions, implementation
from sedbackend.apps.cvs.life_cycle import storage as life_cycle_storage, models as life_cycle_models
from sedbackend.libs.datastructures.pagination import ListChunk
from sedbackend.libs.mysqlutils import MySQLStatementBuilder, Sort, FetchType

DEBUG_ERROR_HANDLING = True #Set to false in production

CVS_VCS_TABLE = 'cvs_vcss'
CVS_VCS_COLUMNS = ['id', 'name', 'description', 'datetime_created', 'year_from', 'year_to', 'project']

CVS_VALUE_DIMENSION_TABLE = 'cvs_value_dimensions'
CVS_VALUE_DIMENSION_COLUMNS = ['id', 'name', 'priority', 'vcs_row']

CVS_VALUE_DRIVER_TABLE = 'cvs_value_drivers'
CVS_VALUE_DRIVER_COLUMNS = ['id', 'vcs', 'name', 'unit']

CVS_VCS_ROW_DRIVERS_TABLE = 'cvs_rowDrivers'
CVS_VCS_ROW_DRIVERS_COLUMNS = ['vcs_row', 'value_driver']

CVS_ISO_PROCESS_TABLE = 'cvs_iso_processes'
CVS_ISO_PROCESS_COLUMNS = ['id', 'name', 'category']

CVS_VCS_SUBPROCESS_TABLE = 'cvs_subprocesses'
CVS_VCS_SUBPROCESS_COLUMNS = ['id', 'name', 'order_index', 'iso_process']

CVS_VCS_STAKEHOLDER_NEED_TABLE = 'cvs_stakeholder_needs'
CVS_VCS_STAKEHOLDER_NEED_COLUMNS = ['id', 'vcs_row', 'need', 'value_dimension', 'rank_weight']

CVS_VCS_ROWS_TABLE = 'cvs_vcs_rows'
CVS_VCS_ROWS_COLUMNS = ['id', 'vcs', 'index', 'stakeholder',
                              'stakeholder_expectations', 'iso_process', 'subprocess']

CVS_VCS_NEED_DRIVERS_TABLE = 'cvs_vcs_need_drivers'
CVS_VCS_NEED_DRIVERS_COLUMNS = ['stakeholder_need', 'value_driver']


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

'''
#Fetches only the value drivers that has a connection with a vcs row.
    query = f'SELECT cvs_value_drivers.id, cvs_value_drivers.name, unit, value_dimension FROM cvs_value_drivers \
            INNER JOIN cvs_rowDrivers ON cvs_value_drivers.id = value_driver \
            INNER JOIN cvs_vcs_rows ON vcs_row = cvs_vcs_rows.id \
            INNER JOIN cvs_vcss ON vcs = cvs_vcss.id \
            WHERE project = %s'         
    with db_connection.cursor(prepared=True) as cursor:
        cursor.execute(query, [project_id])
        res = cursor.fetchall()
        
        res = [dict(zip(cursor.column_names, row)) for row in res]
'''


def get_all_value_driver(db_connection: PooledMySQLConnection, vcs_id: int) -> List[models.ValueDriver]:
    logger.debug(f'Fetching all value drivers for vcs with id={vcs_id}.')

    where_statement = f'vcs = %s'
    where_values = [vcs_id]
    try:
        select_statement = MySQLStatementBuilder(db_connection)
        results = select_statement \
            .select(CVS_VALUE_DRIVER_TABLE, CVS_VALUE_DRIVER_COLUMNS) \
            .where(where_statement, where_values) \
            .order_by(['id'], Sort.ASCENDING) \
            .execute(fetch_type=FetchType.FETCH_ALL, dictionary=True)

    except Error as e:
        logger.debug(f'Error msg: {e.msg}')
        raise exceptions.VCSNotFoundException

    if results is None:
        raise exceptions.ValueDriverNotFoundException

    return [populate_value_driver(result) for result in results]


def get_vcs_need_drivers(db_connection: PooledMySQLConnection, need_id: int) -> List[models.ValueDriver]:
    logger.debug(f'Fetching all value drivers for stakeholder need with id={need_id}.')

    where_statement = f'stakeholder_need = %s'
    where_values = [need_id]

    # TODO: Maybe don't work idk

    select_statement = MySQLStatementBuilder(db_connection)
    results = select_statement \
        .select(CVS_VALUE_DRIVER_TABLE, CVS_VALUE_DRIVER_COLUMNS) \
        .inner_join(CVS_VCS_NEED_DRIVERS_TABLE, 'cvs_vcs_need_drivers.value_driver = cvs_value_drivers.id') \
        .where(where_statement, where_values) \
        .order_by(['cvs_value_drivers.id'], Sort.ASCENDING) \
        .execute(fetch_type=FetchType.FETCH_ALL, dictionary=True)

    return [populate_value_driver(result) for result in results]


def add_vcs_need_driver(db_connection: PooledMySQLConnection, need_id: int, value_driver_id: int) -> bool:
    logger.debug(f'Add value drivers with id={value_driver_id} to stakeholder need with id={need_id}.')

    try:
        insert_statement = MySQLStatementBuilder(db_connection)
        insert_statement \
            .insert(table=CVS_VCS_NEED_DRIVERS_TABLE, columns=CVS_VCS_NEED_DRIVERS_COLUMNS) \
            .set_values([need_id, value_driver_id]) \
            .execute(fetch_type=FetchType.FETCH_NONE)
    except Error as e:
        logger.debug(f'Error msg: {e.msg}')
        raise exceptions.VCSStakeholderNeedNotFound

    return True


def update_vcs_need_driver(db_connection: PooledMySQLConnection, need_id: int, value_drivers: List[int]) -> bool:
    logger.debug(f'Update value drivers in stakeholder need with id={need_id}.')

    delete_statement = MySQLStatementBuilder(db_connection)
    _, rows = delete_statement.delete(CVS_VCS_NEED_DRIVERS_TABLE) \
        .where('stakeholder_need = %s', [need_id]) \
        .execute(return_affected_rows=True)

    [add_vcs_need_driver(db_connection, need_id, value_driver_id) for value_driver_id in value_drivers]

    return True


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


def create_value_driver(db_connection: PooledMySQLConnection, vcs_id: int,
                        value_driver_post: models.ValueDriverPost) -> models.ValueDriver:
    logger.debug(f'Creating a value driver')

    try:
        insert_statement = MySQLStatementBuilder(db_connection)
        insert_statement \
            .insert(table=CVS_VALUE_DRIVER_TABLE, columns=['vcs', 'name', 'unit']) \
            .set_values([vcs_id, value_driver_post.name, value_driver_post.unit]) \
            .execute(fetch_type=FetchType.FETCH_NONE)
        value_driver_id = insert_statement.last_insert_id
    except Error as e:
        logger.debug(f'Error msg: {e.msg}')
        raise exceptions.VCSNotFoundException

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
        set_statement='name = %s, unit = %s',
        values=[new_value_driver.name, new_value_driver.unit],
    )
    update_statement.where('id = %s', [value_driver_id])
    _, rows = update_statement.execute(return_affected_rows=True)

    if rows == 0:
        raise exceptions.ValueDriverFailedToUpdateException

    return get_value_driver(db_connection, value_driver_id)


def delete_value_driver(db_connection: PooledMySQLConnection, value_driver_id: int) -> bool:
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
        vcs_id=db_result['vcs'],
        name=db_result['name'],
        unit=db_result['unit']
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

def get_all_subprocess(db_connection: PooledMySQLConnection, vcs_id: int) -> List[models.VCSSubprocess]:
    logger.debug(f'Fetching all subprocesses for vcs with id={vcs_id}.')
    
    query = f'SELECT cvs_subprocesses.id, cvs_subprocesses.vcs, cvs_subprocesses.name, order_index, \
        cvs_subprocesses.iso_process, cvs_iso_processes.name as iso_process_name, category \
        FROM cvs_subprocesses INNER JOIN cvs_iso_processes ON cvs_subprocesses.iso_process = cvs_iso_processes.id \
        WHERE cvs_subprocesses.vcs = %s'

        #INNER JOIN cvs_vcs_rows ON subprocess = cvs_subprocesses.id'
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

    query = f'SELECT cvs_subprocesses.id, cvs_subprocesses.vcs, cvs_subprocesses.name, order_index, \
        cvs_subprocesses.iso_process, cvs_iso_processes.name as iso_process_name, category \
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


def create_subprocess(db_connection: PooledMySQLConnection, vcs_id: int, subprocess_post: models.VCSSubprocessPost) -> models.VCSSubprocess:
    logger.debug(f'Creating a subprocesses.')

    columns = ['vcs', 'name', 'order_index', 'iso_process']
    values = [vcs_id, subprocess_post.name, subprocess_post.order_index, subprocess_post.parent_process_id]

    insert_statement = MySQLStatementBuilder(db_connection)
    try:
        insert_statement \
            .insert(table=CVS_VCS_SUBPROCESS_TABLE, columns=columns) \
            .set_values(values) \
            .execute(fetch_type=FetchType.FETCH_NONE)
    except Error as e:
        logger.debug(f'Error msg: {e.msg}')

        logger.debug(f'Entire error no: {str(e.errno)}')
        if (DEBUG_ERROR_HANDLING):
            raise exceptions.GenericDatabaseException(e.msg)
        else:
            raise exceptions.ISOProcessNotFoundException #Could also fail if the order index is the same. This is not checked for though. 

    subprocess_id = insert_statement.last_insert_id

    return get_subprocess(db_connection, subprocess_id)


def edit_subprocess(db_connection: PooledMySQLConnection, subprocess_id: int,
                    new_subprocess: models.VCSSubprocessPost) -> models.VCSSubprocess:
    logger.debug(f'Editing subprocesses with id={subprocess_id}.')

    old_subprocess = get_subprocess(db_connection, subprocess_id)
    o = (old_subprocess.name, old_subprocess.parent_process.id)
    n = (new_subprocess.name, new_subprocess.parent_process_id)
    if o == n:  # No change
        return old_subprocess

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

    subprocess = get_subprocess(db_connection, subprocess_id)

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
    update_indices_q = f'UPDATE cvs_subprocesses \
            SET `order_index` = `order_index` - 1 \
            WHERE id = %s and `order_index` > %s'
    with db_connection.cursor(prepared=True) as cursor:
        cursor.execute(update_indices_q, [subprocess_id, subprocess.order_index])

    if rows == 0:
        raise exceptions.SubprocessFailedDeletionException(subprocess_id)

    return True


def populate_subprocess(db_result) -> models.VCSSubprocess:
    logger.debug(f'Populating model for subprocess with id={db_result["id"]}.')
  #  print("in populate: " + db_result['iso_process'])
    return models.VCSSubprocess(
        id=db_result['id'],
        vcs_id=db_result['vcs'],
        name=db_result['name'],
        order_index=db_result['order_index'],
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
# VCS Stakeholder needs
# ======================================================================================================================


def populate_stakeholder_need(db_connection: PooledMySQLConnection, result) -> models.StakeholderNeed:
    logger.debug(f'Populating model for stakeholder need with id={result["id"]}.')
    return models.StakeholderNeed(
        id=result['id'],
        vcs_row_id=result['vcs_row'],
        need=result['need'],
        value_dimension=result['value_dimension'],
        value_drivers=get_vcs_need_drivers(db_connection, result['id']),
        rank_weight=result['rank_weight']
    )


def get_stakeholder_need(db_connection: PooledMySQLConnection, need_id: int) -> models.StakeholderNeed:
    logger.debug(f'Fetching stakeholder need with id={need_id}')

    try:
        select_statement = MySQLStatementBuilder(db_connection)
        result = select_statement \
            .select(CVS_VCS_STAKEHOLDER_NEED_TABLE, CVS_VCS_STAKEHOLDER_NEED_COLUMNS) \
            .where(f'id = %s', [need_id]) \
            .execute(fetch_type=FetchType.FETCH_ONE, dictionary=True)
    except Error as e:
        logger.debug(f'Error msg: {e.msg}')
        raise exceptions.VCSStakeholderNeedNotFound

    return populate_stakeholder_need(db_connection, result)


def get_all_stakeholder_needs(db_connection: PooledMySQLConnection, vcs_row_id: int) -> List[models.StakeholderNeed]:
    logger.debug(f'Fetching all stakeholder needs for vcs row with id={vcs_row_id}')

    try:
        select_statement = MySQLStatementBuilder(db_connection)
        results = select_statement \
            .select(CVS_VCS_STAKEHOLDER_NEED_TABLE, CVS_VCS_STAKEHOLDER_NEED_COLUMNS) \
            .where(f'vcs_row = %s', [vcs_row_id]) \
            .order_by(['id'], Sort.ASCENDING) \
            .execute(fetch_type=FetchType.FETCH_ALL, dictionary=True)

    except Error as e:
        logger.debug(f'Error msg: {e.msg}')
        raise exceptions.VCSTableRowNotFoundException

    return [populate_stakeholder_need(db_connection, result) for result in results]


def create_stakeholder_need(db_connection: PooledMySQLConnection, vcs_row_id: int,
                            need: models.StakeholderNeedPost) -> int:
    logger.debug(f'Creating stakeholder need for vcs row with id={vcs_row_id}')

    need_id = None

    try:
        insert_statement = MySQLStatementBuilder(db_connection)
        insert_statement \
            .insert(table=CVS_VCS_STAKEHOLDER_NEED_TABLE, columns=['vcs_row', 'need', 'value_dimension', 'rank_weight']) \
            .set_values([vcs_row_id, need.need, need.value_dimension, need.rank_weight]) \
            .execute(fetch_type=FetchType.FETCH_NONE)
        need_id = insert_statement.last_insert_id
    except Error as e:
        logger.debug(f'Error msg: {e.msg}')
        # raise exceptions.VCSTableRowNotFoundException

    return need_id


def update_stakeholder_need(db_connection: PooledMySQLConnection, vcs_row_id: int,
                            need: models.StakeholderNeedPost, need_id: int = None) -> models.StakeholderNeed:
    logger.debug(f'Edit stakeholder need for with id={need_id}')

    count = 0
    if need_id:
        count_statement = MySQLStatementBuilder(db_connection)
        count_result = count_statement.count(CVS_VCS_STAKEHOLDER_NEED_TABLE) \
            .where('id = %s', [need_id]) \
            .execute(fetch_type=FetchType.FETCH_ONE, dictionary=True)
        count = count_result['count']

    if need.id and count > 0:
        update_statement = MySQLStatementBuilder(db_connection)
        update_statement.update(
            table=CVS_VCS_STAKEHOLDER_NEED_TABLE,
            set_statement='need = %s, value_dimension = %s, rank_weight = %s',
            values=[need.need, need.value_dimension, need.rank_weight]
        )
        update_statement.where('id = %s', [need_id])
        _, rows = update_statement.execute(return_affected_rows=True)

    else:
        need_id = create_stakeholder_need(db_connection, vcs_row_id, need)

    update_vcs_need_driver(db_connection, need_id, need.value_drivers)

    return get_stakeholder_need(db_connection, need_id)


def delete_stakeholder_need(db_connection: PooledMySQLConnection, need_id: int) -> bool:
    logger.debug(f'Delete stakeholder need with id={need_id}.')

    delete_statement = MySQLStatementBuilder(db_connection)
    _, rows = delete_statement.delete(CVS_VCS_STAKEHOLDER_NEED_TABLE) \
        .where('id = %s', [need_id]) \
        .execute(return_affected_rows=True)

    if rows == 0:
        raise exceptions.VCSStakeholderNeedFailedDeletionException

    return True


# ======================================================================================================================
# VCS Rows
# ======================================================================================================================

def get_vcs_table(db_connection: PooledMySQLConnection, vcs_id: int) -> List[models.VcsRow]:
    logger.debug(f'Fetching all table for VCS with id={vcs_id}.')

    select_statement = MySQLStatementBuilder(db_connection)
    results = select_statement \
        .select(CVS_VCS_ROWS_TABLE, CVS_VCS_ROWS_COLUMNS) \
        .where(f'vcs = %s', [vcs_id]) \
        .order_by(['index'], Sort.ASCENDING) \
        .execute(fetch_type=FetchType.FETCH_ALL, dictionary=True)

    return [populate_vcs_row(db_connection, result) for result in results]


def get_vcs_row(db_connection: PooledMySQLConnection, vcs_row_id: int) -> models.VcsRow:
    logger.debug(f'Fetching a single vcs row with id: {vcs_row_id}')

    select_statement = MySQLStatementBuilder(db_connection)
    result = select_statement \
        .select(CVS_VCS_ROWS_TABLE, CVS_VCS_ROWS_COLUMNS)\
        .where(f'id = %s', [vcs_row_id])\
        .execute(fetch_type=FetchType.FETCH_ONE, dictionary=True)

    return populate_vcs_row(db_connection, result)
    

def populate_vcs_row(db_connection: PooledMySQLConnection, db_result) -> models.VcsRow:
    logger.debug(f'Populating model for table row with id={db_result["id"]}.')

    iso_process, subprocess = None, None
    if db_result['iso_process'] is not None:
        iso_process = get_iso_process(int(db_result['iso_process']), db_connection)
    elif db_result['subprocess'] is not None:
        subprocess = get_subprocess(db_connection, db_result['subprocess_id'])

    return models.VcsRow(
        id=db_result['id'],
        vcs_id=db_result['vcs'],
        index=db_result['index'],
        stakeholder=db_result['stakeholder'],
        stakeholder_expectations=db_result['stakeholder_expectations'],
        stakeholder_needs=get_all_stakeholder_needs(db_connection, db_result['id']),
        iso_process=iso_process,
        subprocess=subprocess
    )


def create_vcs_row(db_connection: PooledMySQLConnection, row: models.VcsRowPost, vcs_id: int) -> int:
    logger.debug(f'Creating row for VCS with id={vcs_id}.')
    values = [row.index, vcs_id, row.stakeholder, row.stakeholder_expectations, row.iso_process,
              row.subprocess]

    vcs_row_id = -1

    insert_statement = MySQLStatementBuilder(db_connection)
    try:
        insert_statement \
            .insert(CVS_VCS_ROWS_TABLE, ['index', 'vcs', 'stakeholder', 'stakeholder_expectations', 'iso_process',
                                         'subprocess']) \
            .set_values(values) \
            .execute(fetch_type=FetchType.FETCH_NONE)
        vcs_row_id = insert_statement.last_insert_id
    except Error as e:
        logger.debug(f'Error msg: {e.msg}')
        '''
        if row.iso_process is not None:
            raise exceptions.ISOProcessNotFoundException
        elif row.subprocess is not None:
            raise exceptions.SubprocessNotFoundException
        else:
            raise exceptions.VCSTableRowFailedToUpdateException(e.msg)
            '''

    if vcs_row_id < 0:
        raise exceptions.VCSTableRowFailedToUpdateException

    return vcs_row_id


def create_vcs_table(db_connection: PooledMySQLConnection, new_vcs_rows: List[models.VcsRowPost], vcs_id: int) -> bool:
    logger.debug(f'Creating table for VCS with id={vcs_id}.')

    for row in new_vcs_rows:

        if row.iso_process is None and row.subprocess is None:
            raise exceptions.VCSTableProcessAmbiguity
        elif row.iso_process is not None and row.subprocess is not None:
            raise exceptions.VCSTableProcessAmbiguity

        vcs_row_id = create_vcs_row(db_connection, row, vcs_id)

        node = life_cycle_models.ProcessNodePost(
            pos_x=0,
            pos_y=0,
            vcs_row=get_vcs_row(db_connection, vcs_row_id)
        )

        life_cycle_storage.create_process_node(db_connection, node, vcs_id)

        [create_stakeholder_need(db_connection, vcs_row_id, need) for need in row.stakeholder_needs]

    return True


def edit_vcs_table(db_connection: PooledMySQLConnection, updated_vcs_rows: List[models.VcsRowPost],
                   vcs_id: int) -> bool:
    logger.debug(f'Editing vcs table')

    new_table_ids = []

    for row in updated_vcs_rows:

        if row.iso_process is None and row.subprocess is None:
            raise exceptions.VCSTableProcessAmbiguity
        elif row.iso_process is not None and row.subprocess is not None:
            raise exceptions.VCSTableProcessAmbiguity

        count = 0
        if row.id:
            count_statement = MySQLStatementBuilder(db_connection)
            count_result = count_statement.count(CVS_VCS_ROWS_TABLE) \
                .where(f'id = %s', [row.id]) \
                .execute(fetch_type=FetchType.FETCH_ONE, dictionary=True)
            count = count_result['count']

        vcs_row_id = row.id

        if row.id and count > 0:
            update_statement = MySQLStatementBuilder(db_connection)
            update_statement.update(
                table=CVS_VCS_ROWS_TABLE,
                set_statement=f'`index` = %s, stakeholder = %s, stakeholder_expectations = %s, iso_process = %s, '
                              f'subprocess = %s, vcs = %s',
                values=[row.index, row.stakeholder, row.stakeholder_expectations, row.iso_process, row.subprocess,
                        vcs_id]
            )
            update_statement.where(f'id = %s', [row.id])
            _, rows = update_statement.execute(return_affected_rows=True)

        else:
            vcs_row_id = create_vcs_row(db_connection, row, vcs_id)
            node = life_cycle_models.ProcessNodePost(
                pos_x=0,
                pos_y=0,
                vcs_row=get_vcs_row(db_connection, vcs_row_id)
            )
            life_cycle_storage.create_process_node(db_connection, node, vcs_id)

        new_table_ids.append(vcs_row_id)

        curr_needs = get_all_stakeholder_needs(db_connection, vcs_row_id)
        new_need_ids = []

        for need in row.stakeholder_needs:
            new_need_ids.append(need.id)
            update_stakeholder_need(db_connection, vcs_row_id, need, need.id)

        for need in curr_needs:
            if need.id not in new_need_ids:
                delete_stakeholder_need(db_connection, need.id)

    curr_table = get_vcs_table(db_connection, vcs_id)

    for row in curr_table:
        if row.id not in new_table_ids:
            delete_statement = MySQLStatementBuilder(db_connection)
            res, rows = delete_statement.delete(CVS_VCS_ROWS_TABLE) \
                .where('id = %s and vcs = %s', [row.id, vcs_id]) \
                .execute(return_affected_rows=True, fetch_type=FetchType.FETCH_ONE)
            if rows == 0:
                raise exceptions.VCSTableRowFailedDeletionException

    return True


def delete_vcs_row(db_connection: PooledMySQLConnection, vcs_row_id: int, vcs_id: int) -> bool:
    logger.debug(f'Deleting vcs row with id: {vcs_row_id}')

    row = get_vcs_row(db_connection, vcs_row_id)
    delete_statement = MySQLStatementBuilder(db_connection)
    res, rows = delete_statement.delete(CVS_VCS_ROWS_TABLE)\
                    .where('id = %s and vcs = %s', [vcs_row_id, vcs_id])\
                    .execute(return_affected_rows=True, fetch_type=FetchType.FETCH_ONE)
    if rows == 0:
        raise exceptions.VCSTableRowFailedDeletionException
    
    update_indices_q = f'UPDATE cvs_vcs_rows \
        SET `index` = `index` - 1 \
        WHERE vcs = %s and `index` > %s'
    with db_connection.cursor(prepared=True) as cursor:
        cursor.execute(update_indices_q, [vcs_id, row.index])

    return True

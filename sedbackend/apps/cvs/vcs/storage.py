from sys import stdout
from typing import List

from fastapi.logger import logger
from mysql.connector.pooling import PooledMySQLConnection

from sedbackend.apps.core.authentication import exceptions as auth_exceptions
from sedbackend.apps.cvs.project.storage import get_cvs_project
from sedbackend.apps.cvs.life_cycle.storage import create_bpmn_node, update_bpmn_node
from sedbackend.apps.cvs.life_cycle.models import NodePost
from sedbackend.apps.cvs.vcs import models, exceptions, implementation
from sedbackend.libs import mysqlutils
from sedbackend.libs.datastructures.pagination import ListChunk
from sedbackend.libs.mysqlutils import MySQLStatementBuilder, Sort, FetchType

CVS_VCS_TABLE = 'cvs_vcss'
CVS_VCS_COLUMNS = ['id', 'name', 'description', 'datetime_created', 'year_from', 'year_to', 'project']

CVS_VCS_VALUE_DRIVER_TABLE = 'cvs_vcs_value_drivers'
CVS_VCS_VALUE_DRIVER_COLUMNS = ['id', 'name', 'unit', 'project_id']

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
# VCS Value driver
# ======================================================================================================================


def get_all_value_driver(db_connection: PooledMySQLConnection, project_id: int,
                         user_id: int) -> ListChunk[models.VCSValueDriver]:
    logger.debug(f'Fetching all value drivers for project with id={project_id}.')

    get_cvs_project(db_connection, project_id, user_id)  # perform checks: project and user

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
    logger.debug(f'Fetching value driver for project with id={value_driver_id}.')

    get_cvs_project(db_connection, project_id, user_id)  # perform checks: project and user

    where_statement = f'id = %s'
    where_values = [value_driver_id]

    select_statement = MySQLStatementBuilder(db_connection)
    result = select_statement \
        .select(CVS_VCS_VALUE_DRIVER_TABLE, CVS_VCS_VALUE_DRIVER_COLUMNS) \
        .where(where_statement, where_values) \
        .execute(fetch_type=FetchType.FETCH_ONE, dictionary=True)

    if result is None:
        raise exceptions.ValueDriverNotFoundException(value_driver_id=value_driver_id)

    value_driver = populate_value_driver(db_connection, result, project_id, user_id)

    return value_driver


def create_value_driver(db_connection: PooledMySQLConnection, value_driver_post: models.VCSValueDriverPost,
                        project_id: int, user_id: int) -> models.VCSValueDriver:
    logger.debug(f'Creating a value driver in project with id={project_id}.')

    get_cvs_project(db_connection, project_id, user_id)  # performs checks for existing project and correct user

    insert_statement = MySQLStatementBuilder(db_connection)
    insert_statement \
        .insert(table=CVS_VCS_VALUE_DRIVER_TABLE, columns=['name', 'unit', 'project_id']) \
        .set_values([value_driver_post.name, value_driver_post.unit, project_id]) \
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
        set_statement='name = %s, unit = %s',
        values=[new_value_driver.name, new_value_driver.unit],
    )
    update_statement.where('id = %s', [value_driver_id])
    _, rows = update_statement.execute(return_affected_rows=True)

    if rows == 0:
        raise exceptions.ValueDriverFailedToUpdateException

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
        raise exceptions.ValueDriverNotFoundException(value_driver_id=value_driver_id)

    if result['project_id'] != project_id:
        raise auth_exceptions.UnauthorizedOperationException

    delete_statement = MySQLStatementBuilder(db_connection)
    _, rows = delete_statement.delete(CVS_VCS_VALUE_DRIVER_TABLE) \
        .where('id = %s', [value_driver_id]) \
        .execute(return_affected_rows=True)

    if rows == 0:
        raise exceptions.ValueDriverFailedDeletionException

    return True


def populate_value_driver(db_connection: PooledMySQLConnection, db_result, project_id: int,
                          user_id: int) -> models.VCSValueDriver:
    return models.VCSValueDriver(
        id=db_result['id'],
        name=db_result['name'],
        unit=db_result['unit'],
        project=get_cvs_project(db_connection, project_id=project_id, user_id=user_id),
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
        .where('id = %s', [iso_process_id]) \
        .execute(FetchType.FETCH_ALL, dictionary=True)
    
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
        iso_process, vcs, cvs_iso_processes.name as iso_process_name, category \
        FROM cvs_subprocesses INNER JOIN cvs_iso_processes ON iso_process = cvs_iso_processes.id\
        WHERE vcs = %s'
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

    columns = ['cvs_subprocesses.id', 'cvs_subprocesses.name', 'order_index', 
    'iso_process', 'cvs_iso_processes.name as iso_process_name', 'category']
  #  select_statement = MySQLStatementBuilder(db_connection)
  #  result = select_statement \
   #     .select(CVS_VCS_SUBPROCESS_TABLE, columns) \
   #     .inner_join(CVS_ISO_PROCESS_TABLE, 'iso_process = cvs_iso_process.id') \
   #     .where('cvs_subprocesses.id = %s', [subprocess_id]) \
   #     .execute(fetch_type=FetchType.FETCH_ONE, dictionary=True)

    query = f'SELECT cvs_subprocesses.id, cvs_subprocesses.name, order_index, \
        iso_process, vcs, cvs_iso_processes.name as iso_process_name, category \
        FROM cvs_subprocesses INNER JOIN cvs_iso_processes ON iso_process = cvs_iso_processes.id\
        WHERE cvs_subprocesses.id = %s'
    with db_connection.cursor(prepared=True) as cursor:
        cursor.execute(query, [subprocess_id])
        last_insert_id = cursor.lastrowid
        res = cursor.fetchone()
        res = dict(zip(cursor.column_names, res))

    if res is None:
        raise exceptions.SubprocessNotFoundException(subprocess_id)

  #  if result['project_id'] != project_id:
  #      raise auth_exceptions.UnauthorizedOperationException

    return populate_subprocess(res)


def create_subprocess(db_connection: PooledMySQLConnection, subprocess_post: models.VCSSubprocessPost) -> models.VCSSubprocess:
    logger.debug(f'Creating a subprocesses.')

    # performing necessary checks
#   get_cvs_project(db_connection, project_id, user_id)
#    get_iso_process(subprocess_post.parent_process_id)

    columns = ['name', 'order_index', 'vcs', 'iso_process']
    values = [subprocess_post.name, subprocess_post.order_index, subprocess_post.vcs_id, subprocess_post.parent_process_id]

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
#    get_iso_process(new_subprocess.parent_process_id)

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
    #        project=get_cvs_project(db_connection, project_id, user_id),


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
# VCS Table
# ======================================================================================================================

#TODO rewrite below
# DO NOT USE IN API CALLS


def get_vcs_table(db_connection: PooledMySQLConnection, vcs_id: int,  user_id: int) -> List[models.VcsRow]:
    logger.debug(f'Fetching all table for VCS with id={vcs_id}.')
#    table_rows = get_all_table_rows(db_connection, vcs_id, user_id)

    select_statement = MySQLStatementBuilder(db_connection)
    results = select_statement \
        .select(CVS_VCS_ROWS_TABLE, CVS_VCS_ROWS_COLUMNS) \
        .where('vcs = %s', [vcs_id]) \
        .order_by(['index'], Sort.ASCENDING) \
        .execute(fetch_type=FetchType.FETCH_ALL, dictionary=True)

    return [populate_vcs_row(db_connection, result, project_id, user_id) for result in results]
    


def get_vcs_table_row(db_connection: PooledMySQLConnection, node_id: int, project_id: int, vcs_id: int,
                      user_id: int) -> models.TableRowGet or None:
    logger.debug(f'Fetching vcs table row with id={node_id}.')

    get_vcs(db_connection, vcs_id, project_id, user_id)  # perform checks for project, vcs and user

    select_statement = MySQLStatementBuilder(db_connection)
    result = select_statement \
        .select(CVS_VCS_TABLE_ROWS_TABLE, CVS_VCS_TABLE_ROWS_COLUMNS) \
        .where('node_id = %s', [node_id]) \
        .execute(fetch_type=FetchType.FETCH_ONE, dictionary=True)

    if result is not None:
        return populate_table_row(db_connection, result, project_id, user_id)
    else:
       return None
        # raise cvs_exceptions.VCSTableRowNotFoundException


def get_all_table_rows(db_connection: PooledMySQLConnection, vcs_id: int, project_id: int,
                       user_id: int) -> List[models.TableRowGet]:
    logger.debug(f'Fetching all table rows for VCS with id={vcs_id}')

    where_statement = f'vcs_id = %s'
    where_values = [vcs_id]

    select_statement = MySQLStatementBuilder(db_connection)
    results = select_statement \
        .select(CVS_VCS_TABLE_ROWS_TABLE, CVS_VCS_TABLE_ROWS_COLUMNS) \
        .where(where_statement, where_values) \
        .order_by(['id'], Sort.ASCENDING) \
        .execute(fetch_type=FetchType.FETCH_ALL, dictionary=True)

    return [populate_table_row(db_connection, result, project_id, user_id) for result in results]


def populate_vcs_row(db_connection: PooledMySQLConnection, db_result, project_id: int,
                       user_id: int) -> models.TableRowGet:
    logger.debug(f'Populating model for table row with id={db_result["id"]}.')

    iso_process, subprocesss = None, None
    if db_result['iso_process_id'] is not None:
        iso_process = get_iso_process(
            db_result['iso_process_id'], db_connection)  # Gets a iso process based on the id that we got from the DB result
    elif db_result['subprocess_id'] is not None:
        try:
            subprocesss = get_subprocess(db_connection, db_result['subprocess_id'])  # Runs a new query on subprocess table based on the id that is in the result of the db query. Why is that not referenced as a foreign key and run as a single query here?????
        except exceptions.SubprocessNotFoundException:
            # If a subprocess is deleted but used in a table, the subprocess wont be found and thus this exception
            pass

    return models.TableRowGet(
        id=db_result['id'],
        node_id=db_result['node_id'],
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
        value_drivers.append(models.ValueDriverGet(id=value_driver.id, name=value_driver.name, unit=value_driver.unit))

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
            raise exceptions.VCSTableRowFailedDeletionException(result['id'])

    # Creating new rows
    for i, table_row in enumerate(new_table.table_rows):

        # Checking processes
        if (table_row.iso_process_id is None) and (table_row.subprocess_id is None):
            # no process provided
            iso_process_id = None
            subprocess_id = None

        elif (table_row.iso_process_id is not None) and (table_row.subprocess_id is not None):
            # two processes provided
            raise exceptions.VCSTableProcessAmbiguity(table_row_id=i)

        elif table_row.iso_process_id is not None:
            # iso process provided

            iso_process = implementation.get_iso_process(table_row.iso_process_id)
            iso_process_id = iso_process.id
            subprocess_id = None
            new_node = NodePost(
                name=iso_process.name,
                node_type="process"
            )
            if (table_row.node_id is None):
                logger.debug(f'Creating new bpmn node')
                node = create_bpmn_node(db_connection, new_node, project_id, vcs_id, user_id)
                table_row.node_id = node.id
            else:
                update_bpmn_node(db_connection, table_row.node_id, new_node, project_id, vcs_id, user_id)

        else:
            # subprocess provided
            iso_process_id = None
            subprocess = implementation.get_subprocess(table_row.subprocess_id, project_id, user_id)
            subprocess_id = subprocess.id
            new_node = NodePost(
                name=subprocess.name,
                node_type="process"
            )
            if (table_row.node_id is None):
                node = create_bpmn_node(db_connection, new_node, project_id, vcs_id, user_id)
                table_row.node_id = node.id
            else:
                update_bpmn_node(db_connection, table_row.node_id, new_node, project_id, vcs_id, user_id)

        # Further checking provided data
        stakeholder = table_row.stakeholder if table_row.stakeholder is not None else ''
        stakeholder_exp = table_row.stakeholder_expectations if table_row.stakeholder_expectations is not None else ''

        columns = ['node_id', 'vcs_id', 'row_index', 'iso_process_id', 'subprocess_id', 'stakeholder',
                   'stakeholder_expectations']
        values = [table_row.node_id, vcs_id, table_row.row_index, iso_process_id, subprocess_id, stakeholder,
                  stakeholder_exp]

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

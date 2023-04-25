from fastapi.logger import logger
from mysql.connector.pooling import PooledMySQLConnection

from sedbackend.libs.mysqlutils import MySQLStatementBuilder, FetchType, Sort
from sedbackend.apps.cvs.life_cycle import exceptions, models
from sedbackend.apps.cvs.vcs import storage as vcs_storage, exceptions as vcs_exceptions
from mysql.connector import Error
from sedbackend.apps.core.files import models as file_models
from sedbackend.apps.core.files import implementation as file_impl

CVS_NODES_TABLE = 'cvs_nodes'
CVS_NODES_COLUMNS = ['cvs_nodes.id', 'vcs', 'from', 'to', 'pos_x', 'pos_y']

CVS_PROCESS_NODES_TABLE = 'cvs_process_nodes'
CVS_PROCESS_NODES_COLUMNS = CVS_NODES_COLUMNS + ['vcs_row']

CVS_START_STOP_NODES_TABLE = 'cvs_start_stop_nodes'
CVS_START_STOP_NODES_COLUMNS = CVS_NODES_COLUMNS + ['type']


# TODO error handling

def populate_process_node(db_connection, project_id, result) -> models.ProcessNodeGet:
    logger.debug(f'Populating model for process node with id={result["id"]} ')

    return models.ProcessNodeGet(
        id=result['id'],
        vcs_id=result['vcs'],
        from_node=result['from'],
        to_node=result['to'],
        pos_x=result['pos_x'],
        pos_y=result['pos_y'],
        vcs_row=vcs_storage.get_vcs_row(db_connection, project_id, result['vcs_row'])
    )


def populate_start_stop_node(result) -> models.StartStopNodeGet:
    logger.debug(f'Populating model for start/stop node with id={result["id"]}')
    return models.StartStopNodeGet(
        id=result['id'],
        vcs_id=result['vcs'],
        from_node=result['from'],
        to_node=result['to'],
        pos_x=result['pos_x'],
        pos_y=result['pos_y'],
        type=result['type']
    )


def get_node(db_connection: PooledMySQLConnection, project_id: int, node_id: int, table=CVS_NODES_TABLE,
             columns=None) -> dict:
    if columns is None:
        columns = CVS_NODES_COLUMNS
    select_statement = MySQLStatementBuilder(db_connection)
    try:
        result = select_statement \
            .select(table, columns) \
            .where('id = %s', [node_id]) \
            .execute(fetch_type=FetchType.FETCH_ONE, dictionary=True)

    except Error as e:
        logger.debug(f'Error msg: {e.msg}')
        raise exceptions.NodeNotFoundException

    vcs_storage.get_vcs(db_connection, result['vcs'], project_id)  # Check if vcs exists and matches project id

    return result


def get_process_node(db_connection: PooledMySQLConnection, project_id: int, node_id: int) -> models.ProcessNodeGet:
    logger.debug(f'Fetching a process node with id={node_id}.')

    select_statement = MySQLStatementBuilder(db_connection)
    try:
        result = select_statement \
            .select(CVS_PROCESS_NODES_TABLE, CVS_PROCESS_NODES_COLUMNS) \
            .inner_join(CVS_NODES_TABLE, 'cvs_nodes.id = cvs_process_nodes.id') \
            .where('cvs_nodes.id = %s', [node_id]) \
            .execute(fetch_type=FetchType.FETCH_ONE, dictionary=True)

    except Error as e:
        logger.debug(f'Error msg: {e.msg}')
        raise exceptions.NodeNotFoundException

    return populate_process_node(db_connection, project_id, result)


def get_start_stop_node(db_connection: PooledMySQLConnection, node_id: int) -> models.StartStopNodeGet:
    logger.debug(f'Fetching a process node with id={node_id}.')

    select_statement = MySQLStatementBuilder(db_connection)
    try:
        result = select_statement \
            .select(CVS_START_STOP_NODES_TABLE, CVS_START_STOP_NODES_COLUMNS) \
            .inner_join(CVS_NODES_TABLE, 'cvs_nodes.id = cvs_start_stop_nodes.id') \
            .where('cvs_nodes.id = %s', [node_id]) \
            .execute(fetch_type=FetchType.FETCH_ONE, dictionary=True)

    except Error as e:
        logger.debug(f'Error msg: {e.msg}')
        raise exceptions.NodeNotFoundException

    return populate_start_stop_node(result)


# Create parent node and return id
def create_node(db_connection: PooledMySQLConnection, vcs_id: int, node: models.NodePost) -> int:
    columns = ['vcs', 'pos_x', 'pos_y']
    values = [vcs_id, node.pos_x, node.pos_y]

    node_id = None
    try:
        insert_statement = MySQLStatementBuilder(db_connection)
        insert_statement \
            .insert(table=CVS_NODES_TABLE, columns=columns) \
            .set_values(values) \
            .execute(fetch_type=FetchType.FETCH_NONE)
        node_id = insert_statement.last_insert_id
    except Error as e:
        logger.debug(f'Error msg: {e.msg}')
        if vcs_id is not None:
            raise vcs_exceptions.VCSNotFoundException

    logger.debug('Created standard node')
    return node_id


def create_process_node(db_connection: PooledMySQLConnection, project_id: int, vcs_id: int,
                        node: models.ProcessNodePost) -> models.ProcessNodeGet:
    logger.debug(f'Create a process node for vcs with id={vcs_id}.')

    node_id = create_node(db_connection, vcs_id, node)

    try:
        insert_statement = MySQLStatementBuilder(db_connection)
        insert_statement \
            .insert(table=CVS_PROCESS_NODES_TABLE, columns=['id', 'vcs_row']) \
            .set_values([node_id, node.vcs_row_id]) \
            .execute(fetch_type=FetchType.FETCH_NONE, return_affected_rows=True)
        # node_id = insert_statement.last_insert_id
        logger.debug(f'Finished process node creation with node id {node_id}')
    except Error as e:
        logger.debug(f'Error msg: {e.msg}')
        raise vcs_exceptions.VCSNotFoundException

    logger.debug('Before getting process node')
    return get_process_node(db_connection, project_id, node_id)


def create_start_stop_node(db_connection: PooledMySQLConnection, node: models.StartStopNodePost,
                           vcs_id: int) -> models.StartStopNodeGet:
    logger.debug(f'Create a process node for vcs with id={vcs_id}.')

    node_id = create_node(db_connection, node, vcs_id)

    columns = ['id', 'type']
    values = [node_id, node.type]

    insert_statement = MySQLStatementBuilder(db_connection)
    try:
        insert_statement \
            .insert(table=CVS_START_STOP_NODES_TABLE, columns=columns) \
            .set_values(values) \
            .execute(fetch_type=FetchType.FETCH_NONE)
    except Error as e:
        logger.debug(f'Error msg: {e.msg}')
        if node.type != "start" and node.type != "stop":
            raise exceptions.InvalidNodeType
        elif vcs_id is not None:
            raise vcs_exceptions.VCSNotFoundException

    return get_start_stop_node(db_connection, node_id)


def delete_node(db_connection: PooledMySQLConnection, project_id: int, node_id: int) -> bool:
    logger.debug(f'Delete node with id={node_id}.')

    get_node(db_connection, project_id, node_id)  # Check if node exists and matches project id

    delete_statement = MySQLStatementBuilder(db_connection)
    _, rows = delete_statement.delete(CVS_NODES_TABLE) \
        .where('id = %s', [node_id]) \
        .execute(return_affected_rows=True)

    if rows == 0:
        raise exceptions.NodeFailedDeletionException(node_id)

    return True


def update_node(db_connection: PooledMySQLConnection, project_id: int, node_id: int, node: models.NodePost) -> bool:
    logger.debug(f'Updating node with id={node_id}.')

    # Performs necessary checks
    get_node(db_connection, project_id, node_id)

    update_statement = MySQLStatementBuilder(db_connection)
    update_statement.update(
        table=CVS_NODES_TABLE,
        set_statement='pos_x = %s, pos_y = %s',
        values=[node.pos_x, node.pos_y],
    )
    update_statement.where('id = %s', [node_id])
    _, rows = update_statement.execute(return_affected_rows=True)
    if rows == 0:
        raise exceptions.NodeFailedToUpdateException

    return True


def get_bpmn(db_connection: PooledMySQLConnection, project_id: int, vcs_id: int) -> models.BPMNGet:
    logger.debug(f'Get BPMN for vcs with id={vcs_id}.')

    vcs_storage.get_vcs(db_connection, project_id, vcs_id)  # Check if vcs exists and matches project id

    where_statement = f'vcs = %s'
    where_values = [vcs_id]

    try:
        select_statement = MySQLStatementBuilder(db_connection)
        process_nodes_result = select_statement \
            .select(CVS_PROCESS_NODES_TABLE, CVS_PROCESS_NODES_COLUMNS) \
            .inner_join(CVS_NODES_TABLE, 'cvs_nodes.id = cvs_process_nodes.id') \
            .where(where_statement, where_values) \
            .order_by(['cvs_nodes.id'], Sort.ASCENDING) \
            .execute(fetch_type=FetchType.FETCH_ALL, dictionary=True)
        process_nodes = [populate_process_node(db_connection, project_id, result) for result in process_nodes_result]

        select_statement = MySQLStatementBuilder(db_connection)
        # start_stop_nodes_result = \
        select_statement \
            .select(CVS_START_STOP_NODES_TABLE, CVS_START_STOP_NODES_COLUMNS) \
            .inner_join(CVS_NODES_TABLE, 'cvs_nodes.id = cvs_start_stop_nodes.id') \
            .where(where_statement, where_values) \
            .order_by(['cvs_nodes.id'], Sort.ASCENDING) \
            .execute(fetch_type=FetchType.FETCH_ALL, dictionary=True)
        # start_stop_nodes = [populate_start_stop_node(result) for result in start_stop_nodes_result]
    except Error as e:
        logger.debug(f'Error msg: {e.msg}')
        raise vcs_exceptions.VCSNotFoundException

    return models.BPMNGet(
        nodes=process_nodes
        # [*process_nodes, *start_stop_nodes]
    )


def update_bpmn(db_connection: PooledMySQLConnection, project_id: int, vcs_id: int,
                bpmn: models.BPMNGet) -> bool:
    logger.debug(f'Updating bpmn with vcs id={vcs_id}.')

    vcs_storage.get_vcs(db_connection, project_id, vcs_id)  # Check if vcs exists and matches project id

    for node in bpmn.nodes:
        updated_node = models.NodePost(
            pos_x=node.pos_x,
            pos_y=node.pos_y
        )
        update_node(db_connection, project_id, node.id, updated_node)

    return True


def save_dsm_file(db_connection: PooledMySQLConnection, project_id: int, 
                  vcs_id: int, file: file_models.StoredFilePost) -> bool:
    
    pass
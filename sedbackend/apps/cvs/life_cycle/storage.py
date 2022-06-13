from typing import List

from fastapi.logger import logger
from mysql.connector.pooling import PooledMySQLConnection

from sedbackend.libs.mysqlutils import MySQLStatementBuilder, FetchType, Sort
from sedbackend.apps.cvs.life_cycle import exceptions, models

CVS_NODES_TABLE = 'cvs_nodes'
CVS_NODES_COLUMNS = ['id', 'vcs', 'from', 'to', 'pos_x', 'pos_y']

CVS_PROCESS_NODES_TABLE = 'cvs_process_nodes'
CVS_PROCESS_NODES_COLUMNS = CVS_NODES_COLUMNS + ['vcs_row']

CVS_START_STOP_NODES_TABLE = 'cvs_start_stop_nodes'
CVS_START_STOP_NODES_COLUMNS = CVS_NODES_COLUMNS + ['type']


# TODO error handling

def populate_process_node(result) -> models.ProcessNodeGet:
    logger.debug(f'Populating model for process node with id={result["id"]}')

    return models.ProcessNodeGet(
        id=result['id'],
        vcs_id=result['vcs_id'],
        from_node=result['from'],
        to_node=result['to'],
        pos_x=result['pos_x'],
        pos_y=result['pos_y'],
        vcs_row=result['vcs_row']  # TODO get vcs row
    )


def populate_start_stop_node(result) -> models.StartStopNodeGet:
    logger.debug(f'Populating model for start/stop node with id={result["id"]}')
    return models.StartStopNodeGet(
        id=result['id'],
        vcs_id=result['vcs_id'],
        from_node=result['from'],
        to_node=result['to'],
        pos_x=result['pos_x'],
        pos_y=result['pos_y'],
        type=result['type']
    )


def get_node(db_connection: PooledMySQLConnection, node_id: int, table=CVS_NODES_TABLE,
             columns=None) -> dict:

    if columns is None:
        columns = CVS_NODES_COLUMNS
    select_statement = MySQLStatementBuilder(db_connection)
    result = select_statement \
        .select(table, columns) \
        .where('id = %s', [node_id]) \
        .execute(fetch_type=FetchType.FETCH_ONE, dictionary=True)

    if result is None:
        raise exceptions.NodeNotFoundException

    return result


def get_process_node(db_connection: PooledMySQLConnection, node_id: int) -> models.ProcessNodeGet:
    logger.debug(f'Fetching a process node with id={node_id}.')
    result = get_node(db_connection, node_id, CVS_PROCESS_NODES_TABLE, CVS_PROCESS_NODES_COLUMNS)
    return populate_process_node(result)


def get_start_stop_node(db_connection: PooledMySQLConnection, node_id: int) -> models.StartStopNodeGet:
    logger.debug(f'Fetching a process node with id={node_id}.')
    result = get_node(db_connection, node_id, CVS_START_STOP_NODES_TABLE, CVS_START_STOP_NODES_COLUMNS)
    return populate_start_stop_node(result)


# Create parent node and return id
def create_node(db_connection: PooledMySQLConnection, node: models.NodePost, vcs_id: int) -> int:
    columns = ['vcs, pos_x, pos_y']
    values = [vcs_id, node.pos_x, node.pos_y]

    insert_statement = MySQLStatementBuilder(db_connection)
    insert_statement \
        .insert(table=CVS_NODES_TABLE, columns=columns) \
        .set_values(values) \
        .execute(fetch_type=FetchType.FETCH_NONE)
    node_id = insert_statement.last_insert_id

    return node_id


def create_process_node(db_connection: PooledMySQLConnection, node: models.ProcessNodePost,
                        vcs_id: int) -> models.ProcessNodeGet:
    logger.debug(f'Create a process node for vcs with id={vcs_id}.')

    node_id = create_node(db_connection, node, vcs_id)

    insert_statement = MySQLStatementBuilder(db_connection)
    insert_statement \
        .insert(table=CVS_PROCESS_NODES_TABLE, columns=['id', 'vcs_row']) \
        .set_values([node_id, node.vcs_row.id]) \
        .execute(fetch_type=FetchType.FETCH_NONE)

    return get_process_node(db_connection, node_id)


def create_start_stop_node(db_connection: PooledMySQLConnection, node: models.StartStopNodePost,
                           vcs_id: int) -> models.StartStopNodeGet:
    logger.debug(f'Create a process node for vcs with id={vcs_id}.')

    node_id = create_node(db_connection, node, vcs_id)

    columns = ['id', 'type']
    values = [node_id, node.type]

    insert_statement = MySQLStatementBuilder(db_connection)
    insert_statement \
        .insert(table=CVS_PROCESS_NODES_TABLE, columns=columns) \
        .set_values(values) \
        .execute(fetch_type=FetchType.FETCH_NONE)
    node_id = insert_statement.last_insert_id

    return get_start_stop_node(db_connection, node_id)


def delete_node(db_connection: PooledMySQLConnection, node_id: int) -> bool:
    logger.debug(f'Delete node with id={node_id}.')

    delete_statement = MySQLStatementBuilder(db_connection)
    _, rows = delete_statement.delete(CVS_NODES_TABLE) \
        .where('id = %s', [node_id]) \
        .execute(return_affected_rows=True)

    if rows == 0:
        raise exceptions.NodeFailedDeletionException(node_id)

    return True


def update_node(db_connection: PooledMySQLConnection, node_id: int, node: models.NodePost) -> bool:
    logger.debug(f'Updating node with id={node_id}.')

    # Performs necessary checks
    get_node(db_connection, node_id)

    update_statement = MySQLStatementBuilder(db_connection)
    update_statement.update(
        table=CVS_NODES_TABLE,
        set_statement='pos_x = %s, pos_y = %s',
        values=[node.pos_x, node.pos_y],
    )
    update_statement.where('id = %s', [node_id])
    _, rows = update_statement.execute(return_affected_rows=True)

    return True


def db_select_nodes(db_connection: PooledMySQLConnection, vcs_id: int, table: str,
                    columns: List) -> dict:
    where_statement = f'vcs = %s'
    where_values = [vcs_id]

    select_statement = MySQLStatementBuilder(db_connection)
    result = select_statement \
        .select(table, columns) \
        .where(where_statement, where_values) \
        .order_by(['id'], Sort.ASCENDING) \
        .execute(fetch_type=FetchType.FETCH_ALL, dictionary=True)

    return result


def get_bpmn(db_connection: PooledMySQLConnection, vcs_id: int) -> models.BPMNGet:
    logger.debug(f'Get BPMN for vcs with id={vcs_id}.')

    # vcs_storage.get_vcs(db_connection, vcs_id, project_id, user_id)  # perform checks: project, vcs and user

    process_nodes_result = db_select_nodes(db_connection, vcs_id, CVS_PROCESS_NODES_TABLE, CVS_PROCESS_NODES_COLUMNS)
    start_stop_nodes_result = db_select_nodes(db_connection, vcs_id, CVS_START_STOP_NODES_TABLE,
                                              CVS_START_STOP_NODES_COLUMNS)

    process_nodes = [populate_process_node(result) for result in process_nodes_result]
    start_stop_nodes = [populate_start_stop_node(result) for result in start_stop_nodes_result]
    return models.BPMNGet(
        nodes=[*process_nodes, *start_stop_nodes]
    )


def update_bpmn(db_connection: PooledMySQLConnection, vcs_id: int,
                bpmn: models.BPMNGet) -> bool:
    logger.debug(f'Updating bpmn with vcs id={vcs_id}.')

    for node in bpmn.nodes:
        new_node = models.NodePost(
            id=node.id,
            pos_x=node.pos_x,
            pos_y=node.pos_y
        )
        update_node(db_connection, node.id, new_node)

    return True

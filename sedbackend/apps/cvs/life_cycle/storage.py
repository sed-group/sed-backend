from typing import List

from fastapi.logger import logger
from mysql.connector.pooling import PooledMySQLConnection

from sedbackend.apps.cvs.vcs import storage as vcs_storage
from sedbackend.libs.mysqlutils import MySQLStatementBuilder, FetchType, Sort
from sedbackend.apps.cvs.life_cycle import exceptions, models

CVS_BPMN_NODES_TABLE = 'cvs_bpmn_nodes'
CVS_BPMN_NODES_COLUMNS = ['id', 'vcs_id', 'name', 'type', 'pos_x', 'pos_y']
CVS_BPMN_EDGES_TABLE = 'cvs_bpmn_edges'
CVS_BPMN_EDGES_COLUMNS = ['id', 'vcs_id', 'name', 'from_node', 'to_node', 'probability']


def populate_bpmn_node(db_connection, result, project_id, user_id) -> models.NodeGet:
    logger.debug(f'Populating model for node with id={result["id"]}.')

    return models.NodeGet(
        id=result['id'],
        vcs_id=result['vcs_id'],
        name=result['name'],
        node_type=result['type'],
        pos_x=result['pos_x'],
        pos_y=result['pos_y'],
        vcs_table_row=vcs_storage.get_vcs_table_row(db_connection, result['id'], project_id, result['vcs_id'], user_id)
    )


def populate_bpmn_edge(result) -> models.EdgeGet:
    logger.debug(f'Populating model for edge with id={result["id"]}.')
    return models.EdgeGet(
        id=result['id'],
        vcs_id=result['vcs_id'],
        name=result['name'],
        from_node=result['from_node'],
        to_node=result['to_node'],
        probability=result['probability']
    )


def get_bpmn_node(db_connection: PooledMySQLConnection, node_id: int, project_id: int,
                  user_id: int) -> models.NodeGet:
    logger.debug(f'Fetching node with id={node_id}.')

    select_statement = MySQLStatementBuilder(db_connection)
    result = select_statement \
        .select(CVS_BPMN_NODES_TABLE, CVS_BPMN_NODES_COLUMNS) \
        .where('id = %s', [node_id]) \
        .execute(fetch_type=FetchType.FETCH_ONE, dictionary=True)

    if result is None:
        raise exceptions.NodeNotFoundException

    return populate_bpmn_node(db_connection, result, project_id, user_id)


def create_bpmn_node(db_connection: PooledMySQLConnection, node: models.NodePost, project_id: int, vcs_id: int,
                     user_id: int) -> models.NodeGet:
    logger.debug(f'Creating a node for vcs with id={vcs_id}.')

    vcs_storage.get_vcs(db_connection, vcs_id, project_id, user_id)  # perform checks: project, vcs and user

    columns = ['vcs_id', 'name', 'type']
    values = [vcs_id, node.name, node.node_type]

    insert_statement = MySQLStatementBuilder(db_connection)
    insert_statement \
        .insert(table=CVS_BPMN_NODES_TABLE, columns=columns) \
        .set_values(values) \
        .execute(fetch_type=FetchType.FETCH_NONE)
    node_id = insert_statement.last_insert_id

    return get_bpmn_node(db_connection, node_id, project_id, user_id)


def delete_bpmn_node(db_connection: PooledMySQLConnection, project_id: int, vcs_id: int, node_id: int, user_id) -> bool:
    logger.debug(f'Delete node with id={node_id}.')

    vcs_storage.get_vcs(db_connection, vcs_id, project_id, user_id)
    get_bpmn_node(db_connection, node_id, project_id, user_id)

    delete_statement = MySQLStatementBuilder(db_connection)
    _, rows = delete_statement.delete(CVS_BPMN_NODES_TABLE) \
        .where('id = %s', [node_id]) \
        .execute(return_affected_rows=True)

    if rows == 0:
        raise exceptions.NodeFailedDeletionException(node_id)

    return True


def update_bpmn_node(db_connection: PooledMySQLConnection, node_id: int, node: models.NodePost, project_id: int,
                     vcs_id: int, user_id: int) -> models.NodeGet:
    logger.debug(f'Updating node with id={node_id}.')

    # Performs necessary checks
    get_bpmn_node(db_connection, node_id, project_id, user_id)

    update_statement = MySQLStatementBuilder(db_connection)
    # Also needs to update the row of the vcs
    update_statement.update(
        table=CVS_BPMN_NODES_TABLE,
        set_statement='vcs_id = %s, name = %s, type = %s, pos_x = %s, pos_y = %s',
        values=[vcs_id, node.name, node.node_type, node.pos_x, node.pos_y],
    )
    update_statement.where('id = %s', [node_id])
    _, rows = update_statement.execute(return_affected_rows=True)

    return get_bpmn_node(db_connection, node_id, project_id, user_id)


def get_bpmn_edge(db_connection: PooledMySQLConnection, edge_id: int) -> models.EdgeGet:
    logger.debug(f'Fetching edge with id={edge_id}.')

    select_statement = MySQLStatementBuilder(db_connection)
    result = select_statement \
        .select(CVS_BPMN_EDGES_TABLE, CVS_BPMN_EDGES_COLUMNS) \
        .where('id = %s', [edge_id]) \
        .execute(fetch_type=FetchType.FETCH_ONE, dictionary=True)

    if result is None:
        raise exceptions.EdgeNotFoundException

    return populate_bpmn_edge(result)


def create_bpmn_edge(db_connection: PooledMySQLConnection, edge: models.EdgePost, project_id: int,
                     vcs_id: int, user_id: int) -> models.EdgeGet:
    logger.debug(f'Creating an edge for vcs with id={vcs_id}.')

    vcs_storage.get_vcs(db_connection, vcs_id, project_id, user_id)  # perform checks: project, vcs and user
    get_bpmn_node(db_connection, edge.from_node, project_id, user_id)
    get_bpmn_node(db_connection, edge.to_node, project_id, user_id)

    columns = ['vcs_id', 'name', 'from_node', 'to_node', 'probability']
    values = [vcs_id, edge.name, edge.from_node, edge.to_node, edge.probability]

    insert_statement = MySQLStatementBuilder(db_connection)
    insert_statement \
        .insert(table=CVS_BPMN_EDGES_TABLE, columns=columns) \
        .set_values(values) \
        .execute(fetch_type=FetchType.FETCH_NONE)
    edge_id = insert_statement.last_insert_id

    return get_bpmn_edge(db_connection, edge_id)


def delete_bpmn_edge(db_connection: PooledMySQLConnection, edge_id: int, project_id: int, vcs_id: int,
                     user_id: int) -> bool:
    get_bpmn_edge(db_connection, edge_id)  # checks
    vcs_storage.get_vcs(db_connection, vcs_id, project_id, user_id)  # perform checks: project, vcs and user

    delete_statement = MySQLStatementBuilder(db_connection)
    _, rows = delete_statement.delete(CVS_BPMN_EDGES_TABLE) \
        .where('id = %s', [edge_id]) \
        .execute(return_affected_rows=True)

    if rows == 0:
        raise exceptions.EdgeFailedDeletionException(edge_id)

    return True


def update_bpmn_edge(db_connection: PooledMySQLConnection, edge_id: int, edge: models.EdgePost,
                     project_id: int, vcs_id: int, user_id: int) -> models.EdgeGet:
    logger.debug(f'Updating edge with id={edge_id}.')

    # Performs necessary checks
    get_bpmn_edge(db_connection, edge_id)
    vcs_storage.get_vcs(db_connection, vcs_id, project_id, user_id)
    get_bpmn_node(db_connection, edge.from_node, project_id, user_id)
    get_bpmn_node(db_connection, edge.to_node, project_id, user_id)

    update_statement = MySQLStatementBuilder(db_connection)
    update_statement.update(
        table=CVS_BPMN_EDGES_TABLE,
        set_statement='vcs_id = %s, name = %s, from_node = %s, to_node = %s, probability = %s',
        values=[vcs_id, edge.name, edge.from_node, edge.to_node, edge.probability],
    )
    update_statement.where('id = %s', [edge_id])
    _, rows = update_statement.execute(return_affected_rows=True)

    return get_bpmn_edge(db_connection, edge_id)


def get_bpmn(db_connection: PooledMySQLConnection, vcs_id: int, project_id: int, user_id: int) -> models.BPMNGet:
    logger.debug(f'Get BPMN for vcs with id={vcs_id}.')

    vcs_storage.get_vcs(db_connection, vcs_id, project_id, user_id)  # perform checks: project, vcs and user

    where_statement = f'vcs_id = %s'
    where_values = [vcs_id]

    select_statement = MySQLStatementBuilder(db_connection)
    nodes = select_statement \
        .select(CVS_BPMN_NODES_TABLE, CVS_BPMN_NODES_COLUMNS) \
        .where(where_statement, where_values) \
        .order_by(['id'], Sort.ASCENDING) \
        .execute(fetch_type=FetchType.FETCH_ALL, dictionary=True)

    select_statement = MySQLStatementBuilder(db_connection)
    edges = select_statement \
        .select(CVS_BPMN_EDGES_TABLE, CVS_BPMN_EDGES_COLUMNS) \
        .where(where_statement, where_values) \
        .order_by(['id'], Sort.ASCENDING) \
        .execute(fetch_type=FetchType.FETCH_ALL, dictionary=True)

    return models.BPMNGet(
        vcs_id=vcs_id,
        nodes=[populate_bpmn_node(db_connection, node, project_id, user_id) for node in nodes],
        edges=[populate_bpmn_edge(edge) for edge in edges],
    )


def update_bpmn(db_connection: PooledMySQLConnection, vcs_id: int, project_id: int, user_id: int,
                nodes: List[models.NodeGet], edges: List[models.EdgeGet]) -> models.BPMNGet:
    logger.debug(f'Updating bpmn with vcs id={vcs_id}.')

    vcs_storage.get_vcs(db_connection, vcs_id, project_id, user_id)  # perform checks: project, vcs and user

    for node in nodes:
        new_node = models.NodePost(
            vcs_id=vcs_id,
            name=node.name,
            node_type=node.node_type,
            pos_x=node.pos_x,
            pos_y=node.pos_y
        )
        update_bpmn_node(db_connection, node.id, new_node, project_id, vcs_id, user_id)

    for edge in edges:
        new_edge = models.EdgePost(
            vcs_id=vcs_id,
            name=edge.name,
            from_node=edge.from_node,
            to_node=edge.to_node,
            probability=edge.probability,
        )
        update_bpmn_edge(db_connection, edge.id, new_edge, project_id, vcs_id, user_id)

    return get_bpmn(db_connection, vcs_id, project_id, user_id)

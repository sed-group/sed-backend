from typing import List

from fastapi.logger import logger
from mysql.connector.pooling import PooledMySQLConnection

from sedbackend.apps.cvs.vcs.storage import get_vcs
from sedbackend.libs.mysqlutils import MySQLStatementBuilder, FetchType, Sort
from sedbackend.apps.cvs.market_input import models, exceptions

CVS_MARKET_INPUT_TABLE = 'cvs_market_input'
CVS_MARKET_INPUT_COLUMN = ['id', 'vcs', 'node', 'time', 'cost', 'revenue']


def populate_market_input(db_result) -> models.MarketInputGet:
    return models.MarketInputGet(
        id=db_result['id'],
        vcs=db_result['vcs'],
        node=db_result['node'],
        time=db_result['time'],
        cost=db_result['cost'],
        revenue=db_result['revenue']
    )


def get_market_input(db_connection: PooledMySQLConnection, node_id: int) -> models.MarketInputGet:
    logger.debug(f'Fetching market input with node id={node_id}.')

    select_statement = MySQLStatementBuilder(db_connection)
    db_result = select_statement \
        .select(CVS_MARKET_INPUT_TABLE, CVS_MARKET_INPUT_COLUMN) \
        .where('node = %s', [node_id]) \
        .execute(fetch_type=FetchType.FETCH_ONE, dictionary=True)

    if db_result is None:
        raise exceptions.MarketInputNotFoundException

    return populate_market_input(db_result)


def get_all_market_input(db_connection: PooledMySQLConnection, vcs_id: int,
                         user_id: int) -> List[models.MarketInputGet]:
    logger.debug(f'Fetching all market inputs for vcs with id={vcs_id}.')

    get_vcs(db_connection, vcs_id, user_id)  # perform checks for existing project, vcs and correct user

    select_statement = MySQLStatementBuilder(db_connection)
    results = select_statement \
        .select(CVS_MARKET_INPUT_TABLE, CVS_MARKET_INPUT_COLUMN) \
        .where('vcs = %s', [vcs_id]) \
        .order_by(['id'], Sort.ASCENDING) \
        .execute(fetch_type=FetchType.FETCH_ALL, dictionary=True)

    return [populate_market_input(db_result) for db_result in results]


def create_market_input(db_connection: PooledMySQLConnection, project_id: int, vcs_id: int, node_id: int,
                        market_input: models.MarketInputPost, user_id: int) -> models.MarketInputGet:
    logger.debug(f'Create market input')

    select_statement = MySQLStatementBuilder(db_connection)
    db_result = select_statement \
        .select(CVS_MARKET_INPUT_TABLE, CVS_MARKET_INPUT_COLUMN) \
        .where('node = %s', [node_id]) \
        .execute(fetch_type=FetchType.FETCH_ONE, dictionary=True)

    if db_result is not None:
        raise exceptions.MarketInputAlreadyExistException

    #get_vcs_table_row(db_connection, node_id, project_id, vcs_id, user_id)  # perform checks

    columns = ['vcs', 'node', 'time', 'cost', 'revenue']
    values = [vcs_id, node_id, market_input.time, market_input.cost, market_input.revenue]

    insert_statement = MySQLStatementBuilder(db_connection)
    insert_statement \
        .insert(table=CVS_MARKET_INPUT_TABLE, columns=columns) \
        .set_values(values) \
        .execute(fetch_type=FetchType.FETCH_NONE)
    # market_input_id = insert_statement.last_insert_id

    return get_market_input(db_connection, node_id)


def update_market_input(db_connection: PooledMySQLConnection, vcs_id: int, node_id: int,
                        market_input: models.MarketInputPost, user_id: int) -> models.MarketInputGet:
    logger.debug(f'Update market input with id={node_id}')

    get_vcs(db_connection, vcs_id, user_id)  # perform checks for existing project, vcs and correct user

    get_market_input(db_connection, node_id)  # Performs necessary checks

    update_statement = MySQLStatementBuilder(db_connection)
    update_statement.update(
        table=CVS_MARKET_INPUT_TABLE,
        set_statement='time = %s, cost = %s, revenue = %s',
        values=[market_input.time, market_input.cost, market_input.revenue],
    )
    update_statement.where('node = %s', [node_id])
    _, rows = update_statement.execute(return_affected_rows=True)

    return get_market_input(db_connection, node_id)

from typing import List

from fastapi.logger import logger
from mysql.connector.pooling import PooledMySQLConnection

from sedbackend.apps.cvs.vcs import storage as vcs_storage
from sedbackend.libs.mysqlutils import MySQLStatementBuilder, FetchType, Sort
from sedbackend.apps.cvs.market_input import models, exceptions
from sedbackend.apps.cvs.life_cycle import storage as life_cycle_storage

CVS_MARKET_INPUT_TABLE = 'cvs_market_input'
CVS_MARKET_INPUT_COLUMN = ['vcs_row', 'time', 'time_unit', 'cost', 'revenue']


def populate_market_input(db_connection, db_result) -> models.MarketInputGet:
    return models.MarketInputGet(
        vcs=db_result['vcs'],
        vcs_row=vcs_storage.get_vcs_row(db_connection, db_result['vcs_row']),
        time=db_result['time'],
        time_unit=db_result['time_unit'],
        cost=db_result['cost'],
        revenue=db_result['revenue']
    )


def get_market_input(db_connection: PooledMySQLConnection, vcs_row_id: int) -> models.MarketInputGet:
    logger.debug(f'Fetching market input with vcs row id={vcs_row_id}.')

    select_statement = MySQLStatementBuilder(db_connection)
    db_result = select_statement \
        .select(CVS_MARKET_INPUT_TABLE, CVS_MARKET_INPUT_COLUMN) \
        .where('vcs_row = %s', [vcs_row_id]) \
        .execute(fetch_type=FetchType.FETCH_ONE, dictionary=True)

    if db_result is None:
        raise exceptions.MarketInputNotFoundException

    return populate_market_input(db_connection, db_result)


def get_all_market_input(db_connection: PooledMySQLConnection, vcs_id: int) -> List[models.MarketInputGet]:
    logger.debug(f'Fetching all market inputs for vcs with id={vcs_id}.')
    columns = ['vcs'] + CVS_MARKET_INPUT_COLUMN

    select_statement = MySQLStatementBuilder(db_connection)
    results = select_statement \
        .select(CVS_MARKET_INPUT_TABLE, columns) \
        .inner_join('cvs_vcs_rows', 'cvs_vcs_rows.id = vcs_row') \
        .where('vcs = %s', [vcs_id]) \
        .order_by(['vcs_row'], Sort.ASCENDING) \
        .execute(fetch_type=FetchType.FETCH_ALL, dictionary=True)

    return [populate_market_input(db_connection, db_result) for db_result in results]

'''
def create_market_input(db_connection: PooledMySQLConnection, vcs_row_id: int,
                        market_input: models.MarketInputPost) -> bool:
    logger.debug(f'Create market input')

    select_statement = MySQLStatementBuilder(db_connection)
    db_result = select_statement \
        .select(CVS_MARKET_INPUT_TABLE, CVS_MARKET_INPUT_COLUMN) \
        .where('vcs_row = %s', [vcs_row_id]) \
        .execute(fetch_type=FetchType.FETCH_ONE, dictionary=True)

    if db_result is not None:
        raise exceptions.MarketInputAlreadyExistException

    vcs_row = vcs_storage.get_vcs_row(db_connection, vcs_row_id)

    columns = ['vcs', 'vcs_row', 'time', 'cost', 'revenue']
    values = [vcs_row.vcs_id, vcs_row_id, market_input.time, market_input.cost, market_input.revenue]

    insert_statement = MySQLStatementBuilder(db_connection)
    insert_statement \
        .insert(table=CVS_MARKET_INPUT_TABLE, columns=columns) \
        .set_values(values) \
        .execute(fetch_type=FetchType.FETCH_NONE)

    return True
'''

def update_market_input(db_connection: PooledMySQLConnection, vcs_row_id: int,
                        market_input: models.MarketInputPost) -> bool:
    logger.debug(f'Update market input with vcs row id={vcs_row_id}')

    select_statement = MySQLStatementBuilder(db_connection)
    db_result = select_statement \
        .select(CVS_MARKET_INPUT_TABLE, CVS_MARKET_INPUT_COLUMN) \
        .where('vcs_row = %s', [vcs_row_id]) \
        .execute(fetch_type=FetchType.FETCH_ONE, dictionary=True)

    if market_input.time_unit.lower() not in ['year', 'month', 'week','day', 'hour']:
        raise exceptions.WrongTimeUnitException(market_input.time_unit)

    if db_result is not None:
        update_statement = MySQLStatementBuilder(db_connection)
        update_statement.update(
            table=CVS_MARKET_INPUT_TABLE,
            set_statement='time = %s, time_unit=%s, cost = %s, revenue = %s',
            values=[market_input.time, market_input.time_unit, market_input.cost, market_input.revenue],
        )
        update_statement.where('vcs_row = %s', [vcs_row_id])
        _, rows = update_statement.execute(return_affected_rows=True)
    else:

        values = [vcs_row_id, market_input.time, market_input.time_unit, market_input.cost, market_input.revenue]

        insert_statement = MySQLStatementBuilder(db_connection)
        insert_statement \
            .insert(table=CVS_MARKET_INPUT_TABLE, columns=CVS_MARKET_INPUT_COLUMN) \
            .set_values(values) \
            .execute(fetch_type=FetchType.FETCH_NONE)

    return True

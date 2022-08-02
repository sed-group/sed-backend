from typing import List

from fastapi.logger import logger
from mysql.connector.pooling import PooledMySQLConnection

from sedbackend.libs.mysqlutils import MySQLStatementBuilder, FetchType, Sort
from sedbackend.apps.cvs.market_input import models, exceptions
from sedbackend.apps.cvs.life_cycle import storage as life_cycle_storage

CVS_MARKET_INPUT_TABLE = 'cvs_market_inputs'
CVS_MARKET_INPUT_COLUMN = ['id', 'project', 'time', 'time_unit', 'cost', 'revenue']


def populate_market_input(db_result) -> models.MarketInputGet:
    return models.MarketInputGet(
        id=db_result['id'],
        name=db_result['name'],
        unit=db_result['unit']
        )


def get_market_input(db_connection: PooledMySQLConnection, market_input_id: int) -> models.MarketInputGet:
    logger.debug(f'Fetching market input with id={market_input_id}.')

    select_statement = MySQLStatementBuilder(db_connection)
    db_result = select_statement \
        .select(CVS_MARKET_INPUT_TABLE, CVS_MARKET_INPUT_COLUMN) \
        .where('id = %s', [market_input_id]) \
        .execute(fetch_type=FetchType.FETCH_ONE, dictionary=True)

    if db_result is None:
        raise exceptions.MarketInputNotFoundException

    return populate_market_input(db_result)


def get_all_market_input(db_connection: PooledMySQLConnection, project_id: int) -> List[models.MarketInputGet]: #TODO join the values to the results
    logger.debug(f'Fetching all market inputs for project with id={project_id}.')

    select_statement = MySQLStatementBuilder(db_connection)
    results = select_statement \
        .select(CVS_MARKET_INPUT_TABLE, CVS_MARKET_INPUT_COLUMN) \
        .where('project = %s', [project_id]) \
        .order_by(['vcs_row'], Sort.ASCENDING) \
        .execute(fetch_type=FetchType.FETCH_ALL, dictionary=True)

    return [populate_market_input(db_result) for db_result in results]

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

def update_market_input(db_connection: PooledMySQLConnection, mi_id: int, project_id: int,
                        market_input: models.MarketInputPost) -> bool:
    logger.debug(f'Update market input with vcs row id={mi_id}')

    select_statement = MySQLStatementBuilder(db_connection)
    db_result = select_statement \
        .select(CVS_MARKET_INPUT_TABLE, CVS_MARKET_INPUT_COLUMN) \
        .where('id = %s', [mi_id]) \
        .execute(fetch_type=FetchType.FETCH_ONE, dictionary=True)

    if db_result is not None:
        update_statement = MySQLStatementBuilder(db_connection)
        update_statement.update(
            table=CVS_MARKET_INPUT_TABLE,
            set_statement='name %s, unit=%s',
            values=[market_input.name, market_input.unit],
        )
        update_statement.where('id = %s', [mi_id])
        _, rows = update_statement.execute(return_affected_rows=True)
    
    else:

        values = [mi_id, project_id, market_input.name, market_input.unit]

        insert_statement = MySQLStatementBuilder(db_connection)
        insert_statement \
            .insert(table=CVS_MARKET_INPUT_TABLE, columns=CVS_MARKET_INPUT_COLUMN) \
            .set_values(values) \
            .execute(fetch_type=FetchType.FETCH_NONE)

    return True

def delete_market_input(db_connection: PooledMySQLConnection, mi_id: int) -> bool:
    logger.debug(f'Deleting market input with id: {mi_id}')

    delete_statement = MySQLStatementBuilder(db_connection)
    _, rows = delete_statement \
        .delete(CVS_MARKET_INPUT_TABLE) \
        .where('id = %s', [mi_id])\
        .execute(fetch_type= FetchType.FETCH_ALL)
    
    if rows != 1:
        raise exceptions.MarketInputFailedDeletionException
    
    return True
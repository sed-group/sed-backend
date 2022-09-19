from typing import List

from fastapi.logger import logger
from mysql.connector.pooling import PooledMySQLConnection

from sedbackend.libs.mysqlutils import MySQLStatementBuilder, FetchType, Sort
from sedbackend.apps.cvs.market_input import models, exceptions

CVS_MARKET_INPUT_TABLE = 'cvs_market_inputs'
CVS_MARKET_INPUT_COLUMN = ['id', 'project', 'name', 'unit']

CVS_MARKET_VALUES_TABLE = 'cvs_market_input_values'
CVS_MARKET_VALUES_COLUMN = ['vcs', 'market_input', 'value']


########################################################################################################################
# Market Input
########################################################################################################################

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


def get_all_market_input(db_connection: PooledMySQLConnection, project_id: int) -> List[
    models.MarketInputGet]:  # TODO join the values to the results
    logger.debug(f'Fetching all market inputs for project with id={project_id}.')

    select_statement = MySQLStatementBuilder(db_connection)
    results = select_statement \
        .select(CVS_MARKET_INPUT_TABLE, CVS_MARKET_INPUT_COLUMN) \
        .where('project = %s', [project_id]) \
        .order_by(['id'], Sort.ASCENDING) \
        .execute(fetch_type=FetchType.FETCH_ALL, dictionary=True)

    return [populate_market_input(db_result) for db_result in results]


def create_market_input(db_connection: PooledMySQLConnection, project_id: int,
                        market_input: models.MarketInputPost) -> models.MarketInputGet:
    logger.debug(f'Create market input')

    insert_statement = MySQLStatementBuilder(db_connection)
    insert_statement \
        .insert(table=CVS_MARKET_INPUT_TABLE, columns=CVS_MARKET_INPUT_COLUMN[1:]) \
        .set_values([project_id, market_input.name, market_input.unit]) \
        .execute(fetch_type=FetchType.FETCH_NONE)

    return get_market_input(db_connection, insert_statement.last_insert_id)


def update_market_input(db_connection: PooledMySQLConnection, market_input_id: int,
                        market_input: models.MarketInputPost) -> bool:
    logger.debug(f'Update market input with vcs row id={market_input_id}')

    update_statement = MySQLStatementBuilder(db_connection)
    update_statement.update(
        table=CVS_MARKET_INPUT_TABLE,
        set_statement='name = %s, unit = %s',
        values=[market_input.name, market_input.unit],
    )
    update_statement.where('id = %s', [market_input_id])
    _, rows = update_statement.execute(return_affected_rows=True)

    return True


def delete_market_input(db_connection: PooledMySQLConnection, mi_id: int) -> bool:
    logger.debug(f'Deleting market input with id: {mi_id}')

    delete_statement = MySQLStatementBuilder(db_connection)
    _, rows = delete_statement \
        .delete(CVS_MARKET_INPUT_TABLE) \
        .where('id = %s', [mi_id]) \
        .execute(fetch_type=FetchType.FETCH_ALL)

    if rows != 1:
        raise exceptions.MarketInputFailedDeletionException

    return True


def get_all_formula_market_inputs(db_connection: PooledMySQLConnection, formulas_id: int) -> List[
    models.MarketInputValue]:
    logger.debug(f'Fetching all market inputs for formulas with vcs_row id: {formulas_id}')

    select_statement = MySQLStatementBuilder(db_connection)
    res = select_statement \
        .select(CVS_MARKET_INPUT_TABLE, CVS_MARKET_INPUT_COLUMN) \
        .inner_join('cvs_formulas_market_inputs', 'market_input = id') \
        .where('formulas = %s', [formulas_id]) \
        .execute(fetch_type=FetchType.FETCH_ALL, dictionary=True)

    if res is None:
        raise exceptions.MarketInputFormulasNotFoundException

    return [populate_market_input(r) for r in res]


########################################################################################################################
# Market Values
########################################################################################################################

def populate_market_input_values(db_result) -> models.MarketInputValue:
    return models.MarketInputValue(
        vcs_id=db_result['vcs'],
        market_input_id=db_result['market_input'],
        value=db_result['value']
    )


def update_market_input_value(db_connection: PooledMySQLConnection, mi_value: models.MarketInputValue) -> bool:
    logger.debug(f'Update market input value')

    count_statement = MySQLStatementBuilder(db_connection)
    count_result = count_statement \
        .count(CVS_MARKET_VALUES_TABLE) \
        .where('vcs = %s AND market_input = %s', [mi_value.vcs_id, mi_value.market_input_id]) \
        .execute(fetch_type=FetchType.FETCH_ONE)
    count = count_result['count']

    if count == 0:
        insert_statement = MySQLStatementBuilder(db_connection)
        insert_statement \
            .insert(table=CVS_MARKET_VALUES_TABLE, columns=CVS_MARKET_VALUES_COLUMN) \
            .set_values([mi_value.vcs_id, mi_value.market_input_id, mi_value.value]) \
            .execute(fetch_type=FetchType.FETCH_NONE)
    else:
        update_statement = MySQLStatementBuilder(db_connection)
        update_statement \
            .update(table=CVS_MARKET_VALUES_TABLE, set_statement='value = %s', values=[mi_value.value]) \
            .where('vcs = %s AND market_input = %s', [mi_value.vcs_id, mi_value.market_input_id]) \
            .execute(fetch_type=FetchType.FETCH_NONE)

    return True


def get_all_market_input_values(db_connection: PooledMySQLConnection, project_id: int) -> List[models.MarketInputValue]:
    logger.debug(f'Fetching all market values for project with id: {project_id}')

    columns = CVS_MARKET_VALUES_COLUMN

    select_statement = MySQLStatementBuilder(db_connection)
    res = select_statement \
        .select(CVS_MARKET_VALUES_TABLE, columns) \
        .inner_join('cvs_market_inputs', 'market_input = cvs_market_inputs.id') \
        .where('project = %s', [project_id]) \
        .execute(fetch_type=FetchType.FETCH_ALL, dictionary=True)

    return [populate_market_input_values(r) for r in res]


def delete_market_value(db_connection: PooledMySQLConnection, vcs_id: int, mi_id: int) -> bool:
    logger.debug(f'Deleting market input value with vcs_id: {vcs_id} and mi_id: {mi_id}')

    delete_statement = MySQLStatementBuilder(db_connection)
    _, rows = delete_statement \
        .delete(CVS_MARKET_VALUES_TABLE) \
        .where('vcs = %s AND market_input = %s', [vcs_id, mi_id]) \
        .execute(fetch_type=FetchType.FETCH_NONE)

    if rows != 1:
        raise exceptions.MarketInputFailedDeletionException

    return True

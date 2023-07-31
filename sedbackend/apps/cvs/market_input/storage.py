from typing import List

from fastapi.logger import logger
from mysql.connector.pooling import PooledMySQLConnection

from mysqlsb import MySQLStatementBuilder, FetchType, Sort
from sedbackend.apps.cvs.market_input import models, exceptions
from sedbackend.apps.cvs.market_input.models import ExternalFactorValue
from sedbackend.apps.cvs.vcs import storage as vcs_storage
from sedbackend.apps.cvs.project import exceptions as project_exceptions

CVS_MARKET_INPUT_TABLE = 'cvs_market_inputs'
CVS_MARKET_INPUT_COLUMN = ['id', 'project', 'name', 'unit']

CVS_MARKET_VALUES_TABLE = 'cvs_market_input_values'
CVS_MARKET_VALUES_COLUMN = ['vcs', 'market_input', 'value']


########################################################################################################################
# Market Input
########################################################################################################################

def populate_external_factor(db_result) -> models.ExternalFactor:
    return models.ExternalFactor(
        id=db_result['id'],
        name=db_result['name'],
        unit=db_result['unit']
    )


def get_external_factor(db_connection: PooledMySQLConnection, project_id: int,
                        external_factor_id: int) -> models.ExternalFactor:
    logger.debug(f'Fetching external factor with id={external_factor_id}.')

    select_statement = MySQLStatementBuilder(db_connection)
    db_result = select_statement \
        .select(CVS_MARKET_INPUT_TABLE, CVS_MARKET_INPUT_COLUMN) \
        .where('id = %s', [external_factor_id]) \
        .execute(fetch_type=FetchType.FETCH_ONE, dictionary=True)

    if db_result is None:
        raise exceptions.ExternalFactorNotFoundException
    if db_result['project'] != project_id:
        raise project_exceptions.CVSProjectNoMatchException

    return populate_external_factor(db_result)


def get_all_external_factors(db_connection: PooledMySQLConnection, project_id: int) -> List[models.ExternalFactor]:
    logger.debug(f'Fetching all external factors for project with id={project_id}.')

    select_statement = MySQLStatementBuilder(db_connection)
    results = select_statement \
        .select(CVS_MARKET_INPUT_TABLE, CVS_MARKET_INPUT_COLUMN) \
        .where('project = %s', [project_id]) \
        .order_by(['id'], Sort.ASCENDING) \
        .execute(fetch_type=FetchType.FETCH_ALL, dictionary=True)

    return [populate_external_factor(db_result) for db_result in results]


def create_external_factor(db_connection: PooledMySQLConnection, project_id: int,
                           external_factor: models.ExternalFactorPost) -> models.ExternalFactor:
    logger.debug(f'Create external factor')

    insert_statement = MySQLStatementBuilder(db_connection)
    insert_statement \
        .insert(table=CVS_MARKET_INPUT_TABLE, columns=CVS_MARKET_INPUT_COLUMN[1:]) \
        .set_values([project_id, external_factor.name, external_factor.unit]) \
        .execute(fetch_type=FetchType.FETCH_NONE)

    return get_external_factor(db_connection, project_id, insert_statement.last_insert_id)


def update_external_factor(db_connection: PooledMySQLConnection, project_id: int,
                           external_factor: models.ExternalFactor) -> bool:
    logger.debug(f'Update external factor with id={external_factor.id}')

    get_external_factor(db_connection, project_id, external_factor.id)  # check if external factor exists and belongs to project

    update_statement = MySQLStatementBuilder(db_connection)
    update_statement.update(
        table=CVS_MARKET_INPUT_TABLE,
        set_statement='name = %s, unit = %s',
        values=[external_factor.name, external_factor.unit],
    )
    update_statement.where('id = %s', [external_factor.id])
    _, rows = update_statement.execute(return_affected_rows=True)

    return True


def delete_external_factor(db_connection: PooledMySQLConnection, project_id: int, external_factor_id: int) -> bool:
    logger.debug(f'Deleting external factor with id: {external_factor_id}')

    get_external_factor(db_connection, project_id, external_factor_id)  # check if external factor exists and belongs to project

    delete_statement = MySQLStatementBuilder(db_connection)
    _, rows = delete_statement \
        .delete(CVS_MARKET_INPUT_TABLE) \
        .where('id = %s', [external_factor_id]) \
        .execute(return_affected_rows=True)

    if rows != 1:
        raise exceptions.ExternalFactorFailedDeletionException

    return True


def get_all_formula_external_factors(db_connection: PooledMySQLConnection,
                                     formulas_id: int) -> List[models.ExternalFactorValue]:
    logger.debug(f'Fetching all external factors for formulas with vcs_row id: {formulas_id}')

    select_statement = MySQLStatementBuilder(db_connection)
    res = select_statement \
        .select(CVS_MARKET_INPUT_TABLE, CVS_MARKET_INPUT_COLUMN) \
        .inner_join('cvs_formulas_market_inputs', 'market_input = id') \
        .where('formulas = %s', [formulas_id]) \
        .execute(fetch_type=FetchType.FETCH_ALL, dictionary=True)

    if res is None:
        raise exceptions.ExternalFactorFormulasNotFoundException

    return [populate_external_factor(r) for r in res]


########################################################################################################################
# External Factor values
########################################################################################################################

def populate_external_factor_values(db_result) -> list[ExternalFactorValue]:
    data_dict = {}

    for item in db_result:
        external_factor = item["market_input"]
        if external_factor not in data_dict:
            data_dict[external_factor] = ExternalFactorValue(
                id=external_factor,
                name=item["name"],
                unit=item["unit"],
                external_factor_values=[
                    {
                        "vcs_id": item["vcs"],
                        "value": item["value"],
                    }
                ],
            )
        else:
            data_dict[external_factor].external_factor_values.append(
                {
                    "vcs_id": item["vcs"],
                    "value": item["value"],
                }
            )

    return list(data_dict.values())


def update_external_factor_value(db_connection: PooledMySQLConnection, project_id: int,
                                 external_factor_value: models.ExternalFactorValue) -> bool:
    logger.debug(f'Update market input value')
    vcs_storage.check_vcs(db_connection, project_id, external_factor_value.vcs_id)  # check if vcs exists
    get_external_factor(db_connection, project_id, external_factor_value.market_input_id)  # check if market input exists

    count_statement = MySQLStatementBuilder(db_connection)
    count_result = count_statement \
        .count(CVS_MARKET_VALUES_TABLE) \
        .where('market_input = %s AND vcs = %s', [mi_value.market_input_id, mi_value.vcs_id]) \
        .execute(fetch_type=FetchType.FETCH_ONE, dictionary=True)
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


def update_external_factor_values(db_connection: PooledMySQLConnection, project_id: int,
                                  ef_values: List[models.ExternalFactorValue]) -> bool:
    logger.debug(f'Update market input values')

    curr_ef_values = get_all_external_factor_values(db_connection, project_id)

    # delete if no longer exists
    for currEFV in curr_ef_values:
        for curr_vcs_val_pair in currEFV.external_factor_values:
            if curr_vcs_val_pair.vcs_id not in [[[v.vcs_id] for v in efv.external_factor_values] for efv in ef_values]:
                delete_market_value(db_connection, project_id, curr_vcs_val_pair.vcs_id, currEFV.id)

    for ef_value in ef_values:
        update_external_factor_value(db_connection, project_id, ef_value)

    return True


def get_all_external_factor_values(db_connection: PooledMySQLConnection,
                                   project_id: int) -> List[models.ExternalFactorValue]:
    logger.debug(f'Fetching all external factors for project with id: {project_id}')

    columns = ['vcs', 'market_input', 'value', 'name', 'unit']

    select_statement = MySQLStatementBuilder(db_connection)
    res = select_statement \
        .select(CVS_MARKET_VALUES_TABLE, columns) \
        .inner_join('cvs_market_inputs', 'market_input = cvs_market_inputs.id') \
        .where('project = %s', [project_id]) \
        .execute(fetch_type=FetchType.FETCH_ALL, dictionary=True)

    return populate_external_factor_values(res)


def delete_market_value(db_connection: PooledMySQLConnection, project_id: int, vcs_id: int, mi_id: int) -> bool:
    logger.debug(f'Deleting market input value with vcs id: {vcs_id} and market input id: {mi_id}')

    get_external_factor(db_connection, project_id, mi_id)  # check if market input exists and belongs to project

    delete_statement = MySQLStatementBuilder(db_connection)
    _, rows = delete_statement \
        .delete(CVS_MARKET_VALUES_TABLE) \
        .where('vcs = %s AND market_input = %s', [vcs_id, mi_id]) \
        .execute(return_affected_rows=True)

    if rows != 1:
        raise exceptions.ExternalFactorFailedDeletionException

    return True

from typing import List

from fastapi.logger import logger
from mysql.connector.pooling import PooledMySQLConnection

from mysqlsb import MySQLStatementBuilder, FetchType, Sort
from sedbackend.apps.cvs.market_input import models, exceptions
from sedbackend.apps.cvs.market_input.models import ExternalFactorValue, VcsEFValuePair, ExternalFactor, \
    ExternalFactorPost
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

    get_external_factor(db_connection, project_id,
                        external_factor.id)  # check if external factor exists and belongs to project

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

    get_external_factor(db_connection, project_id,
                        external_factor_id)  # check if external factor exists and belongs to project

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
                external_factor_values=[],
            )
        if item["vcs"] is not None and item["value"] is not None:
            data_dict[external_factor].external_factor_values.append(
                VcsEFValuePair(vcs_id=item["vcs"], value=item["value"])
            )
    return list(data_dict.values())


def update_external_factor_value(db_connection: PooledMySQLConnection, project_id: int,
                                 external_factor_value: models.ExternalFactorValue) -> bool:
    logger.debug(f'Update external factor value')

    if len(external_factor_value.external_factor_values) == 0:
        return True
    prepared_values = []
    prepared_statement = ''
    for index, value in enumerate(external_factor_value.external_factor_values):
        if index != len(external_factor_value.external_factor_values) - 1:
            prepared_statement += '(%s, %s, %s),'
        else:
            prepared_statement += '(%s, %s, %s)'
        prepared_values += [value.vcs_id, external_factor_value.id, value.value]

    query = f'INSERT INTO cvs_market_input_values (vcs, market_input, value) \
    VALUES ' + prepared_statement + ' ON DUPLICATE KEY UPDATE value = VALUES(value);'

    with db_connection.cursor(prepared=True) as cursor:
        res = cursor.execute(query, prepared_values)
        logger.debug(res)

    return True


def compare_and_delete_external_factor_values(db_connection: PooledMySQLConnection, project_id: int,
                                              prev_ef_values: List[models.ExternalFactorValue],
                                              new_ef_values: List[models.ExternalFactorValue]):
    # Delete external factor values that does not exist in the new table but did in the previous one
    efv_dict2 = {efv.id: {vcs_pair.vcs_id for vcs_pair in efv.external_factor_values} for efv in new_ef_values}
    logger.debug(efv_dict2)
    for efv in prev_ef_values:
        parent_id = efv.id
        if parent_id in efv_dict2:
            vcs_ids_set1 = {vcs_pair.vcs_id for vcs_pair in efv.external_factor_values}
            vcs_ids_set2 = efv_dict2[parent_id]
            for vcs_id in vcs_ids_set1 - vcs_ids_set2:
                delete_external_factor_value(db_connection, project_id, vcs_id, parent_id)

    return True


def sync_new_external_factors(db_connection: PooledMySQLConnection, project_id: int,
                              prev_ef_values: List[models.ExternalFactorValue],
                              new_ef_values: List[models.ExternalFactorValue]):
    ef_ids_to_remove = {efv.id for efv in prev_ef_values} - {efv.id for efv in new_ef_values}
    for ef_remove_id in ef_ids_to_remove:
        delete_external_factor(db_connection, project_id, ef_remove_id)
    updated_ef_values = [efv for efv in prev_ef_values if efv.id not in ef_ids_to_remove]

    for new_efv in new_ef_values:
        matching_efv = next((efv for efv in updated_ef_values if efv.id == new_efv.id), None)
        if matching_efv:
            if matching_efv.name != new_efv.name or matching_efv.unit != new_efv.unit:
                update_external_factor(db_connection, project_id,
                                       ExternalFactor(id=new_efv.id, name=new_efv.name, unit=new_efv.unit))
        else:
            new_ef = create_external_factor(db_connection, project_id,
                                            ExternalFactorPost(name=new_efv.name, unit=new_efv.unit))
            updated_ef_values.append(ExternalFactorValue(id=new_ef.id, name=new_ef.name, unit=new_ef.unit,
                                                         external_factor_values=new_efv.external_factor_values))
    return updated_ef_values


def update_external_factor_values(db_connection: PooledMySQLConnection, project_id: int,
                                  ef_values: List[models.ExternalFactorValue]) -> bool:
    logger.debug(f'Update external factor values for project={project_id}')

    old_ef_values = get_all_external_factor_values(db_connection, project_id)

    compare_and_delete_external_factor_values(db_connection, project_id, old_ef_values, ef_values)

    # Add, update or remove External Factors that has changed since previously
    ef_values_new_ids = sync_new_external_factors(db_connection, project_id, old_ef_values, ef_values)

    # Update values for External factors
    for ef_value in ef_values_new_ids:
        update_external_factor_value(db_connection, project_id, ef_value)

    return True


def get_all_external_factor_values(db_connection: PooledMySQLConnection,
                                   project_id: int) -> List[models.ExternalFactorValue]:
    logger.debug(f'Fetching all external factors for project with id: {project_id}')

    query = f'SELECT vcs, cvs_market_inputs.id AS market_input, value, name, unit \
            FROM cvs_market_inputs \
            LEFT JOIN cvs_market_input_values ON cvs_market_input_values.market_input = cvs_market_inputs.id \
            WHERE cvs_market_inputs.project = %s;'

    with db_connection.cursor(prepared=True, dictionary=True) as cursor:
        cursor.execute(query, [project_id])
        res = cursor.fetchall()

    return populate_external_factor_values(res)


def delete_external_factor_value(db_connection: PooledMySQLConnection, project_id: int, vcs_id: int,
                                 ef_id: int) -> bool:
    logger.debug(f'Deleting external factor value with vcs id: {vcs_id} and market input id: {ef_id}')

    get_external_factor(db_connection, project_id, ef_id)  # check if market input exists and belongs to project

    delete_statement = MySQLStatementBuilder(db_connection)
    _, rows = delete_statement \
        .delete(CVS_MARKET_VALUES_TABLE) \
        .where('vcs = %s AND market_input = %s', [vcs_id, ef_id]) \
        .execute(return_affected_rows=True)

    if rows != 1:
        raise exceptions.ExternalFactorFailedDeletionException

    return True

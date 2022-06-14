from typing import List

from fastapi.logger import logger
from mysql.connector.pooling import PooledMySQLConnection

from sedbackend.apps.cvs.vcs.storage import get_value_driver
from sedbackend.libs.mysqlutils import MySQLStatementBuilder, FetchType, Sort
from sedbackend.apps.cvs.design import models, exceptions

DESIGNS_TABLE = 'cvs_designs'
DESIGNS_COLUMNS = ['id', 'project', 'vcs', 'name', 'description']

QUANTIFIED_OBJECTIVE_TABLE = 'cvs_quantified_objectives'
QUANTIFIED_OBJECTIVE_COLUMNS = ['id', 'design', 'value_driver', 'name', 'value', 'unit']


def create_design(db_connection: PooledMySQLConnection, design_post: models.DesignPost, vcs_id: int) -> models.Design:
    logger.debug(f'creating design with vcs_id={vcs_id}')

    insert_statement = MySQLStatementBuilder(db_connection)
    insert_statement \
        .insert(table=DESIGNS_TABLE, columns=['vcs', 'name', 'description']) \
        .set_values([vcs_id, design_post.name, design_post.description]) \
        .execute(fetch_type=FetchType.FETCH_NONE)
    design_id = insert_statement.last_insert_id

    return get_design(db_connection, design_id)


def get_design(db_connection: PooledMySQLConnection, design_id: int) -> models.Design:
    select_statement = MySQLStatementBuilder(db_connection)

    result = select_statement \
        .select(DESIGNS_TABLE, DESIGNS_COLUMNS) \
        .where('id = %s', [design_id]) \
        .execute(fetch_type=FetchType.FETCH_ONE, dictionary=True)

    if result is None:
        raise exceptions.DesignNotFoundException

    return populate_design(result)


def get_all_designs(db_connection: PooledMySQLConnection, vcs_id: int) -> List[models.Design]:
    logger.debug(f'Fetching all Designs with vcs_id={vcs_id}')

    select_statement = MySQLStatementBuilder(db_connection)
    results = select_statement \
        .select(DESIGNS_TABLE, DESIGNS_COLUMNS) \
        .where('vcs = %s', [vcs_id]) \
        .order_by(['id'], Sort.ASCENDING) \
        .execute(fetch_type=FetchType.FETCH_ALL, dictionary=True)

    design_list = []
    for result in results:
        design_list.append(populate_design(result))

    return design_list


def delete_design(db_connection: PooledMySQLConnection, design_id: int) -> bool:
    logger.debug(f'Deleting design with id={design_id}')

    select_statement = MySQLStatementBuilder(db_connection)
    result = select_statement \
        .select(DESIGNS_TABLE, DESIGNS_COLUMNS) \
        .where('id = %s', [design_id]) \
        .execute(fetch_type=FetchType.FETCH_ONE, dictionary=True)

    if result is None:
        raise exceptions.DesignNotFoundException

    if delete_all_quantified_objectives(db_connection, design_id):
        pass
    else:
        raise exceptions.QuantifiedObjectivesNotDeleted

    delete_statement = MySQLStatementBuilder(db_connection)
    _, rows = delete_statement.delete(DESIGNS_TABLE) \
        .where('id = %s', [design_id]) \
        .execute(return_affected_rows=True)

    if rows == 0:
        raise exceptions.DesignNotFoundException

    return True


def edit_design(db_connection: PooledMySQLConnection, design_id: int,
                updated_design: models.DesignPost) -> models.Design:
    logger.debug(f'Editing Design with id = {design_id}')

    update_statement = MySQLStatementBuilder(db_connection)
    update_statement.update(
        table=DESIGNS_TABLE,
        set_statement='name = %s, description = %s',
        values=[updated_design.name, updated_design.description]
    )
    update_statement.where('id = %s', [design_id])
    _, rows = update_statement.execute(return_affected_rows=True)

    if rows == 0:
        raise exceptions.DesignNotFoundException

    return get_design(db_connection, design_id)


def populate_design(db_result) -> models.Design:
    return models.Design(
        id=db_result['id'],
        vcs=db_result['vcs'],
        name=db_result['name'],
        description=db_result['description']
    )


def get_quantified_objective(db_connection: PooledMySQLConnection,
                             quantified_objective_id: int) -> models.QuantifiedObjective:
    logger.debug(f'Get quantified objective with id = {quantified_objective_id}')

    select_statement = MySQLStatementBuilder(db_connection)
    result = select_statement \
        .select(QUANTIFIED_OBJECTIVE_TABLE, QUANTIFIED_OBJECTIVE_COLUMNS) \
        .where('id = %s', [quantified_objective_id]) \
        .execute(fetch_type=FetchType.FETCH_ONE, dictionary=True)

    if result is None:
        raise exceptions.QuantifiedObjectiveNotFoundException

    return populate_qo(db_connection, result)


def get_all_quantified_objectives(db_connection: PooledMySQLConnection,
                                  design_id: int) -> List[models.QuantifiedObjective]:
    logger.debug(f'Get all quantified objectives for design with id = {design_id}')

    select_statement = MySQLStatementBuilder(db_connection)
    res = select_statement \
        .select(QUANTIFIED_OBJECTIVE_TABLE, QUANTIFIED_OBJECTIVE_COLUMNS) \
        .where('design = %s', [design_id]) \
        .execute(fetch_type=FetchType.FETCH_ALL, dictionary=True)

    if res is None:
        raise exceptions.QuantifiedObjectiveNotFoundException

    qo_list = []

    for result in res:
        qo_list.append(populate_qo(db_connection, result))

    return qo_list


def create_quantified_objective(db_connection: PooledMySQLConnection, design_id: int, value_driver_id: int,
                                quantified_objective_post: models.QuantifiedObjectivePost) \
        -> models.QuantifiedObjective:
    logger.debug(f'Create quantified objective for design with id = {design_id}')

    get_design(db_connection, design_id)
    get_value_driver(db_connection, value_driver_id)

    insert_statement = MySQLStatementBuilder(db_connection)
    insert_statement \
        .insert(table=QUANTIFIED_OBJECTIVE_TABLE, columns=['design', 'value_driver', 'name', 'property', 'unit']) \
        .set_values([design_id, value_driver_id, quantified_objective_post.name, quantified_objective_post.value,
                     quantified_objective_post.unit]) \
        .execute(fetch_type=FetchType.FETCH_NONE)
    quantified_id = insert_statement.last_insert_id

    return get_quantified_objective(db_connection, quantified_id)


def delete_quantified_objective(db_connection: PooledMySQLConnection, quantified_objective_id: int) -> bool:
    logger.debug(f'Delete quantified objectives with id = {quantified_objective_id}')

    select_statement = MySQLStatementBuilder(db_connection)
    result = select_statement \
        .select(QUANTIFIED_OBJECTIVE_TABLE, QUANTIFIED_OBJECTIVE_COLUMNS) \
        .where('id = %s', [quantified_objective_id]) \
        .execute(fetch_type=FetchType.FETCH_ONE, dictionary=True)

    if result is None:
        raise exceptions.QuantifiedObjectiveNotFoundException

    delete_statement = MySQLStatementBuilder(db_connection)
    _, rows = delete_statement.delete(QUANTIFIED_OBJECTIVE_TABLE) \
        .where('id = %s', [quantified_objective_id]) \
        .execute(return_affected_rows=True)

    if rows == 0:
        raise exceptions.QuantifiedObjectiveNotFoundException

    return True


# Do not open up for api. Should only be used when deleting other table entries.
def delete_all_quantified_objectives(db_connection: PooledMySQLConnection, design_id: int) -> bool:
    logger.debug(f'Deleting all quantified objectives with design id = {design_id}')

    delete_statement = MySQLStatementBuilder(db_connection)
    _, rows = delete_statement.delete(QUANTIFIED_OBJECTIVE_TABLE) \
        .where('design = %s', [design_id]) \
        .execute(return_affected_rows=True)

    return True


def edit_quantified_objective(db_connection: PooledMySQLConnection, quantified_objective_id: int,
                              updated_qo: models.QuantifiedObjectivePost) -> models.QuantifiedObjective:
    logger.debug(f'Editing quantified objective with id = {quantified_objective_id}')

    update_statement = MySQLStatementBuilder(db_connection)
    update_statement.update(
        table=QUANTIFIED_OBJECTIVE_TABLE,
        set_statement='name = %s, property = %s, unit = %s',
        values=[updated_qo.name, updated_qo.value, updated_qo.unit]
    )
    update_statement.where('id = %s', [quantified_objective_id])
    _, rows = update_statement.execute(return_affected_rows=True)

    if rows == 0:
        raise exceptions.QuantifiedObjectiveNotFoundException

    return get_quantified_objective(db_connection, quantified_objective_id)


def populate_qo(db_connection: PooledMySQLConnection, db_result) -> models.QuantifiedObjective:
    return models.QuantifiedObjective(
        id=db_result['id'],
        design=db_result['design'],
        value_driver=get_value_driver(db_connection, db_result['value_driver']),
        name=db_result['name'],
        value=db_result['value'],
        unit=db_result['unit'],
    )

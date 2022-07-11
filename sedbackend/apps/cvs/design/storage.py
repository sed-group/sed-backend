from typing import List

from fastapi.logger import logger
from mysql.connector.pooling import PooledMySQLConnection

from sedbackend.apps.cvs.vcs.storage import get_value_driver
from sedbackend.libs.mysqlutils import MySQLStatementBuilder, FetchType, Sort
from sedbackend.apps.cvs.design import models, exceptions

DESIGN_GROUPS_TABLE = 'cvs_design_groups'
DESIGN_GROUPS_COLUMNS = ['id', 'vcs', 'name']

DESIGNS_TABLE = 'cvs_designs'
DESIGNS_COLUMNS = ['id', 'vcs', 'design_group', 'name']

QUANTIFIED_OBJECTIVE_TABLE = 'cvs_quantified_objectives'
QUANTIFIED_OBJECTIVE_COLUMNS = ['design_group', 'value_driver', 'name', 'unit']

QUANTIFIED_OBJECTIVE_VALUE_TABLE = 'cvs_quantified_objective_values'
QUANTIFIED_OBJECTIVE_VALUE_COLUMNS = ['design', 'design_group', 'value_driver', 'value']


def create_design_group(db_connection: PooledMySQLConnection, design_group: models.DesignGroupPost,
                        vcs_id: int) -> models.DesignGroup:
    logger.debug(f'creating design group with vcs_id={vcs_id}')

    insert_statement = MySQLStatementBuilder(db_connection)
    insert_statement \
        .insert(table=DESIGN_GROUPS_TABLE, columns=['vcs', 'name']) \
        .set_values([vcs_id, design_group.name]) \
        .execute(fetch_type=FetchType.FETCH_NONE)
    design_id = insert_statement.last_insert_id

    return get_design_group(db_connection, design_id)


def get_design_group(db_connection: PooledMySQLConnection, design_group_id: int) -> models.DesignGroup:
    select_statement = MySQLStatementBuilder(db_connection)

    result = select_statement \
        .select(DESIGN_GROUPS_TABLE, DESIGN_GROUPS_COLUMNS) \
        .where('id = %s', [design_group_id]) \
        .execute(fetch_type=FetchType.FETCH_ONE, dictionary=True)

    if result is None:
        raise exceptions.DesignGroupNotFoundException

    return populate_design_group(db_connection, result)


def get_all_design_groups(db_connection: PooledMySQLConnection, vcs_id: int) -> List[models.DesignGroup]:
    logger.debug(f'Fetching all design groups with vcs_id={vcs_id}')

    select_statement = MySQLStatementBuilder(db_connection)
    results = select_statement \
        .select(DESIGN_GROUPS_TABLE, DESIGN_GROUPS_COLUMNS) \
        .where('vcs = %s', [vcs_id]) \
        .order_by(['id'], Sort.ASCENDING) \
        .execute(fetch_type=FetchType.FETCH_ALL, dictionary=True)

    design_list = []
    for result in results:
        design_list.append(populate_design_group(db_connection, result))

    return design_list


def delete_design_group(db_connection: PooledMySQLConnection, design_group_id: int) -> bool:
    logger.debug(f'Deleting design group with id={design_group_id}')

    delete_statement = MySQLStatementBuilder(db_connection)
    _, rows = delete_statement.delete(DESIGN_GROUPS_TABLE) \
        .where('id = %s', [design_group_id]) \
        .execute(return_affected_rows=True)

    if rows == 0:
        raise exceptions.DesignNotFoundException

    return True


def edit_design_group(db_connection: PooledMySQLConnection, design_group_id: int,
                      design_group: models.DesignGroupPost) -> models.DesignGroup:
    logger.debug(f'Editing Design with id = {design_group_id}')

    update_statement = MySQLStatementBuilder(db_connection)
    update_statement.update(
        table=DESIGNS_TABLE,
        set_statement='name = %s',
        values=[design_group.name]
    )
    update_statement.where('id = %s', [design_group_id])
    _, rows = update_statement.execute(return_affected_rows=True)

    if rows == 0:
        raise exceptions.DesignNotFoundException

    # TODO update qo values

    return get_design_group(db_connection, design_group_id)


def populate_design_group(db_connection, db_result) -> models.DesignGroup:
    return models.DesignGroup(
        id=db_result['id'],
        vcs=db_result['vcs'],
        name=db_result['name'],
        qo_list=get_all_quantified_objectives(db_connection, db_result['id'])
    )


def populate_qo_value(db_result) -> models.QuantifiedObjectiveValue:
    return models.QuantifiedObjectiveValue(
        design_id=db_result['design'],
        value_driver_id=db_result['value_driver'],
        design_group_id=db_result['design_group'],
        value=db_result['value']
    )


def get_qo_value(db_connection: PooledMySQLConnection, design_id: int, value_driver_id: int):
    logger.debug(f'Get quantified objective value for value driver with id = {value_driver_id}'
                 f'and design with id = {design_id}')

    select_statement = MySQLStatementBuilder(db_connection)
    result = select_statement \
        .select(QUANTIFIED_OBJECTIVE_VALUE_TABLE, QUANTIFIED_OBJECTIVE_VALUE_COLUMNS) \
        .where('value_driver = %s and design = %s', [value_driver_id, design_id]) \
        .execute(fetch_type=FetchType.FETCH_ONE, dictionary=True)

    if result is None:
        raise exceptions.QuantifiedObjectiveValueNotFoundException

    return populate_qo_value(result)


def create_qo_value(db_connection: PooledMySQLConnection, design_group_id: int, design_id: int, value_driver_id: int,
                    qo: models.QuantifiedObjectiveValuePost) -> models.QuantifiedObjectiveValue:
    logger.debug(f'Create quantified objective value for value driver with id = {value_driver_id}'
                 f'and design with id = {design_id}')

    insert_statement = MySQLStatementBuilder(db_connection)
    insert_statement \
        .insert(table=QUANTIFIED_OBJECTIVE_VALUE_TABLE, columns=QUANTIFIED_OBJECTIVE_VALUE_COLUMNS) \
        .set_values([design_id, design_group_id, value_driver_id, qo.value, qo]) \
        .execute(fetch_type=FetchType.FETCH_NONE)

    return get_qo_value(db_connection, design_id, value_driver_id)


def edit_qo_value(db_connection: PooledMySQLConnection, design_group_id: int, design_id: int, value_driver_id: int,
                  qo: models.QuantifiedObjectiveValuePost) -> models.QuantifiedObjectiveValue:
    update_statement = MySQLStatementBuilder(db_connection)
    update_statement.update(
        table=QUANTIFIED_OBJECTIVE_VALUE_TABLE,
        set_statement='value = %s',
        values=[qo.value]
    )
    update_statement.where('value_driver = %s and design = %s and design_group = %s',
                           [value_driver_id, design_id, design_group_id])
    _, rows = update_statement.execute(return_affected_rows=True)

    return get_qo_value(db_connection, design_id, value_driver_id)


def get_quantified_objective(db_connection: PooledMySQLConnection,
                             value_driver_id: int, design_group_id: int) -> models.QuantifiedObjective:
    logger.debug(f'Get quantified objective for value driver with id = {value_driver_id} '
                 f'in design group with id = {design_group_id}')

    select_statement = MySQLStatementBuilder(db_connection)
    result = select_statement \
        .select(QUANTIFIED_OBJECTIVE_TABLE, QUANTIFIED_OBJECTIVE_COLUMNS) \
        .where('value_driver = %s and design_group = %s', [value_driver_id, design_group_id]) \
        .execute(fetch_type=FetchType.FETCH_ONE, dictionary=True)

    if result is None:
        raise exceptions.QuantifiedObjectiveNotFoundException

    return populate_qo(db_connection, result)


def get_all_quantified_objectives(db_connection: PooledMySQLConnection,
                                  design_group_id: int) -> List[models.QuantifiedObjective]:
    logger.debug(f'Get all quantified objectives for design group with id = {design_group_id}')

    select_statement = MySQLStatementBuilder(db_connection)
    res = select_statement \
        .select(QUANTIFIED_OBJECTIVE_TABLE, QUANTIFIED_OBJECTIVE_COLUMNS) \
        .where('design_group = %s', [design_group_id]) \
        .execute(fetch_type=FetchType.FETCH_ALL, dictionary=True)

    if res is None:
        raise exceptions.QuantifiedObjectiveNotFoundException

    qo_list = []

    for result in res:
        qo_list.append(populate_qo(db_connection, result))

    return qo_list


def create_quantified_objective(db_connection: PooledMySQLConnection, design_group_id: int, value_driver_id: int,
                                quantified_objective_post: models.QuantifiedObjectivePost) \
        -> bool:
    logger.debug(f'Create quantified objective for value driver with id = {value_driver_id} '
                 f'in design group with id = {design_group_id}')

    get_design_group(db_connection, design_group_id)
    get_value_driver(db_connection, value_driver_id)

    insert_statement = MySQLStatementBuilder(db_connection)
    insert_statement \
        .insert(table=QUANTIFIED_OBJECTIVE_TABLE, columns=['design_group', 'value_driver', 'name', 'unit']) \
        .set_values([design_group_id, value_driver_id, quantified_objective_post.name,
                     quantified_objective_post.unit]) \
        .execute(fetch_type=FetchType.FETCH_NONE)

    return True


def delete_quantified_objective(db_connection: PooledMySQLConnection, value_driver_id: int,
                                design_group_id: int) -> bool:
    logger.debug(f'Delete quantified objectives with value driver id = {value_driver_id} '
                 f'and design group id = {design_group_id}')

    delete_statement = MySQLStatementBuilder(db_connection)
    _, rows = delete_statement.delete(QUANTIFIED_OBJECTIVE_TABLE) \
        .where('value_driver = %s and design_group = %s', [value_driver_id, design_group_id]) \
        .execute(return_affected_rows=True)

    if rows == 0:
        raise exceptions.QuantifiedObjectiveNotFoundException

    return True


def edit_quantified_objective(db_connection: PooledMySQLConnection, value_driver_id: int, design_group_id: int,
                              updated_qo: models.QuantifiedObjectivePost) -> models.QuantifiedObjective:
    logger.debug(f'Editing quantified objective for value driver with id = {value_driver_id} '
                 f'in design group with id = {design_group_id}')

    update_statement = MySQLStatementBuilder(db_connection)
    update_statement.update(
        table=QUANTIFIED_OBJECTIVE_TABLE,
        set_statement='name = %s, unit = %s',
        values=[updated_qo.name, updated_qo.unit]
    )
    update_statement.where('value_driver = %s and design_group = %s', [value_driver_id, design_group_id])
    _, rows = update_statement.execute(return_affected_rows=True)

    if rows == 0:
        raise exceptions.QuantifiedObjectiveNotFoundException

    return get_quantified_objective(db_connection, value_driver_id, design_group_id)


def populate_qo(db_connection: PooledMySQLConnection, db_result) -> models.QuantifiedObjective:
    return models.QuantifiedObjective(
        design_group=db_result['design_group'],
        value_driver=get_value_driver(db_connection, db_result['value_driver']),
        name=db_result['name'],
        unit=db_result['unit'],
    )

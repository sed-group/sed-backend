from typing import List
from mysql.connector import Error
from fastapi.logger import logger
from mysql.connector.pooling import PooledMySQLConnection
from sedbackend.apps.cvs.project.exceptions import CVSProjectNotFoundException, CVSProjectNoMatchException
from sedbackend.apps.cvs.vcs.models import ValueDriver
from sedbackend.apps.cvs.vcs import storage as vcs_storage
from sedbackend.apps.cvs.vcs.storage import CVS_VALUE_DRIVER_COLUMNS, CVS_VALUE_DRIVER_TABLE, populate_value_driver
from mysqlsb import MySQLStatementBuilder, FetchType, Sort
from sedbackend.apps.cvs.design import models, exceptions

DESIGN_GROUPS_TABLE = 'cvs_design_groups'
DESIGN_GROUPS_COLUMNS = ['id', 'project', 'name']

DESIGN_GROUP_DRIVER_TABLE = 'cvs_design_group_drivers'
DESIGN_GROUP_DRIVER_COLUMNS = ['design_group', 'value_driver']

DESIGNS_TABLE = 'cvs_designs'
DESIGNS_COLUMNS = ['id', 'design_group', 'name']

VD_DESIGN_VALUES_TABLE = 'cvs_vd_design_values'
VD_DESIGN_VALUES_COLUMNS = ['value_driver', 'design', 'value']


def create_design_group(db_connection: PooledMySQLConnection, project_id: int,
                        design_group: models.DesignGroupPost) -> models.DesignGroup:
    logger.debug(f'creating design group in project={project_id}')

    insert_statement = MySQLStatementBuilder(db_connection)
    insert_statement \
        .insert(table=DESIGN_GROUPS_TABLE, columns=['project', 'name']) \
        .set_values([project_id, design_group.name]) \
        .execute(fetch_type=FetchType.FETCH_NONE)
    design_group_id = insert_statement.last_insert_id

    if design_group_id is None or design_group_id < 0:
        raise CVSProjectNotFoundException

    if design_group.vcs_id is not None:
        value_drivers = vcs_storage.get_all_value_driver_vcs(db_connection, project_id, design_group.vcs_id)
        [add_vd_to_design_group(db_connection, design_group_id, vd.id) for vd in value_drivers]

    return get_design_group(db_connection, project_id, design_group_id)


def add_vd_to_design_group(db_connection: PooledMySQLConnection, design_group_id: int, vd_id: int) -> bool:
    try:
        insert_statement = MySQLStatementBuilder(db_connection)
        insert_statement \
            .insert(table=DESIGN_GROUP_DRIVER_TABLE, columns=DESIGN_GROUP_DRIVER_COLUMNS) \
            .set_values([design_group_id, vd_id]) \
            .execute(fetch_type=FetchType.FETCH_NONE)
    except Exception as e:
        logger.debug(f'{e.__class__}, {e}')
        raise exceptions.DesignGroupInsertException

    return True


def get_design_group(db_connection: PooledMySQLConnection, project_id: int, design_group_id: int) -> models.DesignGroup:
    select_statement = MySQLStatementBuilder(db_connection)

    result = select_statement \
        .select(DESIGN_GROUPS_TABLE, DESIGN_GROUPS_COLUMNS) \
        .where('id = %s', [design_group_id]) \
        .execute(fetch_type=FetchType.FETCH_ONE, dictionary=True)

    if result is None:
        raise exceptions.DesignGroupNotFoundException
    if result['project'] != project_id:
        raise CVSProjectNoMatchException

    value_drivers = get_all_drivers_design_group(db_connection, result['id'])
    result.update({'vds': value_drivers})
    return populate_design_group(result)


def get_all_design_groups(db_connection: PooledMySQLConnection, project_id: int) -> List[models.DesignGroup]:
    logger.debug(f'Fetching all design groups for project={project_id}')

    select_statement = MySQLStatementBuilder(db_connection)
    results = select_statement \
        .select(DESIGN_GROUPS_TABLE, DESIGN_GROUPS_COLUMNS) \
        .where('project = %s', [project_id]) \
        .order_by(['id'], Sort.ASCENDING) \
        .execute(fetch_type=FetchType.FETCH_ALL, dictionary=True)

    design_list = []
    for result in results:
        value_drivers = get_all_drivers_design_group(db_connection, result['id'])
        result.update({'vds': value_drivers})

        design_list.append(populate_design_group(result))

    return design_list


def delete_design_group(db_connection: PooledMySQLConnection, project_id: int, design_group_id: int) -> bool:
    logger.debug(f'Deleting design group with id={design_group_id}')

    get_design_group(db_connection, project_id, design_group_id)  # Check if design group exists and matches project

    delete_statement = MySQLStatementBuilder(db_connection)
    _, rows = delete_statement.delete(DESIGN_GROUPS_TABLE) \
        .where('id = %s', [design_group_id]) \
        .execute(return_affected_rows=True)

    if rows == 0:
        raise exceptions.DesignNotFoundException

    return True


def edit_design_group(db_connection: PooledMySQLConnection, project_id: int, design_group_id: int,
                      design_group: models.DesignGroupPut) -> models.DesignGroup:
    logger.debug(f'Editing Design with id = {design_group_id}')

    # Check if design group exists in DB and matches project
    curr_design_group = get_design_group(db_connection, project_id, design_group_id)

    try:
        update_statement = MySQLStatementBuilder(db_connection)
        update_statement.update(
            table=DESIGN_GROUPS_TABLE,
            set_statement='name = %s',
            values=[design_group.name]
        )
        update_statement.where('id = %s', [design_group_id])
        _, rows = update_statement.execute(return_affected_rows=True)
    except Exception as e:
        logger.debug(f'{e.__class__}, {e}')
        raise exceptions.DesignGroupNotFoundException

    vds = [vd.id for vd in curr_design_group.vds]

    to_delete = list(filter(lambda x: x not in design_group.vd_ids, vds))

    if design_group.vd_ids:
        to_add = list(filter(lambda x: x not in vds, design_group.vd_ids))
        for vd_id in to_add:
            add_vd_to_design_group(db_connection, design_group_id, vd_id)

    if to_delete is not None:
        for vd_id in to_delete:
            delete_statement = MySQLStatementBuilder(db_connection)
            delete_statement.delete(DESIGN_GROUP_DRIVER_TABLE) \
                .where('design_group = %s and value_driver = %s', [design_group_id, vd_id]) \
                .execute(fetch_type=FetchType.FETCH_NONE)

    return get_design_group(db_connection, project_id, design_group_id)


def populate_design_group(db_result) -> models.DesignGroup:
    return models.DesignGroup(
        id=db_result['id'],
        name=db_result['name'],
        vds=db_result['vds']
    )


def populate_design_with_values(db_result) -> models.Design:
    return models.Design(
        id=db_result['id'],
        name=db_result['name'],
        design_group_id=db_result['design_group'],
        vd_design_values=db_result['vd_values']
    )

def populate_design(db_result) -> models.Design:
    return models.Design(
        id=db_result['id'],
        name=db_result['name'],
        design_group_id=db_result['design_group']
    )


def get_design(db_connection: PooledMySQLConnection, design_id: int):
    logger.debug(f'Get design with id = {design_id}')
    select_statement = MySQLStatementBuilder(db_connection)
    result = select_statement \
        .select(DESIGNS_TABLE, DESIGNS_COLUMNS) \
        .where('id = %s', [design_id]) \
        .execute(fetch_type=FetchType.FETCH_ONE, dictionary=True)

    if result is None:
        raise exceptions.DesignNotFoundException

    vd_design_values = get_all_vd_design_values(db_connection, result['id'])
    result.update({'vd_values': vd_design_values})

    return populate_design_with_values(result)


def get_designs(db_connection: PooledMySQLConnection, project_id: int, design_group_id: int) -> List[models.Design]:
    logger.debug(f'Get all designs in design group with id = {design_group_id}')

    get_design_group(db_connection, project_id, design_group_id)  # Check if design group exists and matches project

    try:
        select_statement = MySQLStatementBuilder(db_connection)
        res = select_statement \
            .select(DESIGNS_TABLE, DESIGNS_COLUMNS) \
            .where('design_group = %s', [design_group_id]) \
            .execute(fetch_type=FetchType.FETCH_ALL, dictionary=True)
    except Error as e:
        logger.debug(f'Error msg: {e.msg}')
        raise exceptions.DesignGroupNotFoundException

    designs = []
    for result in res:
        vd_design_values = get_all_vd_design_values(db_connection, result['id'])
        result.update({'vd_values': vd_design_values})
        designs.append(populate_design_with_values(result))

    return designs


def get_all_designs(db_connection: PooledMySQLConnection, design_group_ids: List[int]) -> List[models.Design]:
    logger.debug(f'Get all designs in design groups with ids = {design_group_ids}')

    try:
        query = f'SELECT cvs_designs.id, cvs_designs.design_group, cvs_designs.name \
                    FROM cvs_designs \
                    WHERE cvs_designs.design_group IN ({",".join(["%s" for _ in range(len(design_group_ids))])})'
        with db_connection.cursor(prepared=True) as cursor:
            cursor.execute(query, design_group_ids)
            res = cursor.fetchall()
            res = [dict(zip(cursor.column_names, row)) for row in res]
    except Error as e:
        logger.debug(f'Error msg: {e.msg}')
        raise exceptions.DesignGroupNotFoundException

    designs = []
    for result in res:
        vd_design_values = get_all_vd_design_values(db_connection, result['id'])
        result.update({'vd_values': vd_design_values})
        designs.append(populate_design_with_values(result))

    return designs


def create_design(db_connection: PooledMySQLConnection, design_group_id: int,
                  design: models.DesignPost) -> bool:
    logger.debug(f'Create a design for design group with id = {design_group_id}')

    insert_statement = MySQLStatementBuilder(db_connection)
    insert_statement \
        .insert(table=DESIGNS_TABLE, columns=['design_group', 'name']) \
        .set_values([design_group_id, design.name]) \
        .execute(fetch_type=FetchType.FETCH_NONE)
    design_id = insert_statement.last_insert_id

    if design.vd_design_values is not None:
        [add_value_to_design_vd(db_connection, design_id, d_val.vd_id, d_val.value) for d_val in
         design.vd_design_values]

    return True


def edit_design(db_connection: PooledMySQLConnection, design: models.DesignPut) -> bool:
    logger.debug(f'Edit design with id = {design.id}')
    design_id = design.id

    try:
        update_statement = MySQLStatementBuilder(db_connection)
        update_statement.update(
            table=DESIGNS_TABLE,
            set_statement='name = %s',
            values=[design.name]
        )
        update_statement.where('id = %s', [design_id])
        _, rows = update_statement.execute(return_affected_rows=True)
    except Error as e:
        logger.debug(f'Error msg: {e.msg}')
        raise exceptions.DesignNotFoundException

    vd_values = get_all_vd_design_values(db_connection, design_id)

    if vd_values is not None:
        for val in vd_values:
            delete_statement = MySQLStatementBuilder(db_connection)
            delete_statement.delete(VD_DESIGN_VALUES_TABLE) \
                .where('value_driver = %s AND design = %s', [val.vd_id, design_id]) \
                .execute(fetch_type=FetchType.FETCH_NONE)

    for val in design.vd_design_values:
        add_value_to_design_vd(db_connection, design_id, val.vd_id, val.value)

    return True


def add_value_to_design_vd(db_connection: PooledMySQLConnection, design_id: int, vd_id: int, value: float) -> bool:
    try:
        insert_statement = MySQLStatementBuilder(db_connection)
        insert_statement \
            .insert(table=VD_DESIGN_VALUES_TABLE, columns=VD_DESIGN_VALUES_COLUMNS) \
            .set_values([vd_id, design_id, value]) \
            .execute(fetch_type=FetchType.FETCH_NONE)
    except Exception as e:
        logger.debug(f'{e.__class__}, {e}')
        raise exceptions.DesignInsertException

    return True


# Edit design if exists, otherwise create a new one. Delete if not longer used
def edit_designs(db_connection: PooledMySQLConnection, project_id: int, design_group_id: int,
                 designs: List[models.DesignPut]) -> bool:
    logger.debug(f'Edit designs with design group id = {design_group_id}')

    # Check if design group exists and matches project
    curr_designs = get_designs(db_connection, project_id, design_group_id)
    for design in curr_designs:
        if design.id not in [d.id for d in designs]:
            delete_design(db_connection, design.id)

    for design in designs:
        count = 0
        if design.id:
            count_statement = MySQLStatementBuilder(db_connection)
            count_result = count_statement.count(DESIGNS_TABLE) \
                .where(f'id = %s', [design.id]) \
                .execute(fetch_type=FetchType.FETCH_ONE, dictionary=True)
            count = count_result['count']

        if count == 0:
            create_design(db_connection, design_group_id,
                          models.DesignPost(name=design.name, vd_design_values=design.vd_design_values))
        else:
            edit_design(db_connection, design)

    return True


def delete_design(db_connection: PooledMySQLConnection, design_id: int) -> bool:
    logger.debug(f'Delete design with id = {design_id}')

    delete_statement = MySQLStatementBuilder(db_connection)
    _, rows = delete_statement.delete(DESIGNS_TABLE) \
        .where('id = %s', [design_id]) \
        .execute(return_affected_rows=True)

    if rows == 0:
        raise exceptions.QuantifiedObjectiveNotFoundException

    return True


# TODO Add error handling when selecting value drivers
def get_all_drivers_design_group(db_connection: PooledMySQLConnection, design_group_id: int) -> List[ValueDriver]:
    logger.debug(f'Fetching all value drivers for design group {design_group_id}')

    columns = DESIGN_GROUP_DRIVER_COLUMNS + CVS_VALUE_DRIVER_COLUMNS
    select_statement = MySQLStatementBuilder(db_connection)
    res = select_statement \
        .select(DESIGN_GROUP_DRIVER_TABLE, columns) \
        .inner_join('cvs_value_drivers', 'value_driver = id') \
        .where('design_group = %s', [design_group_id]) \
        .execute(fetch_type=FetchType.FETCH_ALL, dictionary=True)

    vds = [populate_value_driver(r) for r in res]

    return vds


# TODO add error handling
def get_all_vd_design_values(db_connection: PooledMySQLConnection,
                             design_id: int) -> List[models.ValueDriverDesignValue]:
    logger.debug(f'Fetching all vd design values for design: {design_id}')

    select_statement = MySQLStatementBuilder(db_connection)
    res = select_statement \
        .select(VD_DESIGN_VALUES_TABLE, VD_DESIGN_VALUES_COLUMNS) \
        .where('design = %s', [design_id]) \
        .execute(fetch_type=FetchType.FETCH_ALL, dictionary=True)

    values = []
    for result in res:
        val = models.ValueDriverDesignValue(
            vd_id=result['value_driver'],
            value=result['value']
        )
        values.append(val)

    return values


def get_all_formula_value_drivers(db_connection: PooledMySQLConnection, formula_id: int) -> List[models.ValueDriver]:
    logger.debug(f'Fetching all value drivers for formulas with vcs_row: {formula_id}')

    columns = CVS_VALUE_DRIVER_COLUMNS
    select_statement = MySQLStatementBuilder(db_connection)
    res = select_statement \
        .select(CVS_VALUE_DRIVER_TABLE, columns) \
        .inner_join('cvs_formulas_value_drivers',
                    'cvs_formulas_value_drivers.value_driver = id') \
        .where('formulas = %s', [formula_id]) \
        .execute(fetch_type=FetchType.FETCH_ALL, dictionary=True)

    if res is None:
        raise exceptions.QuantifiedObjectiveNotInFormulas

    return [populate_value_driver(r) for r in res]

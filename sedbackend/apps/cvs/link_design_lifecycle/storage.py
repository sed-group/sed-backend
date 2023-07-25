from typing import List

from fastapi.logger import logger
from mysql.connector.pooling import PooledMySQLConnection

from sedbackend.apps.cvs.design.storage import get_design_group
from sedbackend.apps.cvs.vcs.storage import get_vcs_row
from sedbackend.apps.cvs.vcs.storage import get_vcs
from sedbackend.apps.cvs.vcs import exceptions as vcs_exceptions
from sedbackend.apps.cvs.link_design_lifecycle import models, exceptions
from mysqlsb import FetchType, MySQLStatementBuilder

CVS_FORMULAS_TABLE = 'cvs_design_mi_formulas'
CVS_FORMULAS_COLUMNS = ['project', 'vcs_row', 'design_group', 'time', 'time_unit', 'cost', 'revenue', 'rate']

CVS_FORMULAS_VALUE_DRIVERS_TABLE = 'cvs_formulas_value_drivers'
CVS_FORMULAS_VALUE_DRIVERS_COLUMNS = ['vcs_row', 'design_group', 'value_driver']

CVS_FORMULAS_EXTERNAL_FACTORS_TABLE = 'cvs_formulas_external_factors'
CVS_FORMULAS_EXTERNAL_FACTORS_COLUMNS = ['vcs_row', 'design_group', 'external_factor']


def create_formulas(db_connection: PooledMySQLConnection, vcs_row_id: int, design_group_id: int,
                    formulas: models.FormulaPost) -> bool:
    logger.debug(f'Creating formulas')

    values = [vcs_row_id, design_group_id, formulas.time, formulas.time_unit.value, formulas.cost, formulas.revenue,
              formulas.rate.value]

    try:
        insert_statement = MySQLStatementBuilder(db_connection)
        insert_statement \
            .insert(table=CVS_FORMULAS_TABLE, columns=CVS_FORMULAS_COLUMNS) \
            .set_values(values=values) \
            .execute(fetch_type=FetchType.FETCH_NONE)
    except Exception as e:
        logger.error(f'Error while inserting formulas: {e}')
        raise exceptions.FormulasFailedUpdateException

    add_value_driver_formulas(db_connection, vcs_row_id, design_group_id, formulas.value_drivers)
    add_external_factor_formulas(db_connection, vcs_row_id, design_group_id, formulas.external_factors)

    return True


def add_value_driver_formulas(db_connection: PooledMySQLConnection, vcs_row_id: int, design_group_id: int,
                              value_drivers: List[int]):
    try:
        prepared_list = []
        insert_statement = f'INSERT INTO {CVS_FORMULAS_VALUE_DRIVERS_TABLE} (vcs_row, design_group, value_driver) VALUES'
        for value_driver_id in value_drivers:
            insert_statement += f'(%s, %s, %s),'
            prepared_list.append(vcs_row_id)
            prepared_list.append(design_group_id)
            prepared_list.append(value_driver_id)
        with db_connection.cursor(prepared=True) as cursor:
            cursor.execute(insert_statement[:-1], prepared_list)
    except Exception as e:
        logger.error(f'Error while inserting value drivers: {e}')
        raise exceptions.FormulasFailedUpdateException


def delete_value_driver_formulas(db_connection: PooledMySQLConnection, vcs_row_id: int, design_group_id: int,
                                 value_drivers: List[int]):
    delete_statement = MySQLStatementBuilder(db_connection)
    _, rows = delete_statement \
        .delete(CVS_FORMULAS_VALUE_DRIVERS_TABLE) \
        .where('vcs_row = %s and design_group = %s and value_driver in %s',
               [vcs_row_id, design_group_id, value_drivers]) \
        .execute(return_affected_rows=True)


def add_external_factor_formulas(db_connection: PooledMySQLConnection, vcs_row_id: int, design_group_id: int,
                                 external_factors: List[int]):
    try:
        prepared_list = []
        insert_statement = f'INSERT INTO {CVS_FORMULAS_EXTERNAL_FACTORS_TABLE} (vcs_row, design_group, market_input) VALUES'
        for external_factor_id in external_factors:
            insert_statement += f'(%s, %s, %s),'
            prepared_list.append(vcs_row_id)
            prepared_list.append(design_group_id)
            prepared_list.append(external_factor_id)
        with db_connection.cursor(prepared=True) as cursor:
            cursor.execute(insert_statement[:-1], prepared_list)
    except Exception as e:
        logger.error(f'Error while inserting external factors: {e}')
        raise exceptions.FormulasFailedUpdateException


def delete_external_factor_formulas(db_connection: PooledMySQLConnection, vcs_row_id: int, design_group_id: int,
                                    external_factors: List[int]):
    delete_statement = MySQLStatementBuilder(db_connection)
    _, rows = delete_statement \
        .delete(CVS_FORMULAS_EXTERNAL_FACTORS_TABLE) \
        .where('vcs_row = %s and design_group = %s and external_factors in %s',
               [vcs_row_id, design_group_id, external_factors]) \
        .execute(return_affected_rows=True)


def edit_formulas(db_connection: PooledMySQLConnection, project_id: int, vcs_row_id: int, design_group_id: int,
                  formulas: models.FormulaPost) -> bool:
    get_design_group(db_connection, project_id, design_group_id)  # Check if design group exists and matches project
    get_vcs_row(db_connection, project_id, vcs_row_id)

    count_statement = MySQLStatementBuilder(db_connection)
    count = count_statement.count(CVS_FORMULAS_TABLE) \
        .where('vcs_row = %s and design_group = %s', [vcs_row_id, design_group_id]) \
        .execute(fetch_type=FetchType.FETCH_ONE, dictionary=True)
    count = count['count']

    logger.debug(f'count: {count}')

    if count == 0:
        create_formulas(db_connection, vcs_row_id, design_group_id, formulas)
    elif count == 1:
        logger.debug(f'Editing formulas')
        columns = CVS_FORMULAS_COLUMNS[3:]
        set_statement = ', '.join([col + ' = %s' for col in columns])

        values = [formulas.time, formulas.time_unit.value, formulas.cost, formulas.revenue, formulas.rate.value]

        update_statement = MySQLStatementBuilder(db_connection)
        _, rows = update_statement \
            .update(table=CVS_FORMULAS_TABLE, set_statement=set_statement, values=values) \
            .where('vcs_row = %s and design_group = %s', [vcs_row_id, design_group_id]) \
            .execute(return_affected_rows=True)

        where_statement = "vcs_row = %s and design_group = %s and " \
                          "value_driver IN (" + ",".join(["%s" for _ in range(len(formulas.value_drivers))]) + ")"
        select_statement = MySQLStatementBuilder(db_connection)
        value_driver_res = select_statement.select(CVS_FORMULAS_VALUE_DRIVERS_TABLE, CVS_FORMULAS_VALUE_DRIVERS_COLUMNS) \
            .where(where_statement, [vcs_row_id, design_group_id] + formulas.value_drivers) \
            .execute(fetch_type=FetchType.FETCH_ALL, dictionary=True)

        delete_value_drivers = [value_driver_id['id'] for value_driver_id in value_driver_res if value_driver_id not in
                                formulas.value_drivers]
        add_value_drivers = [value_driver_id for value_driver_id in formulas.value_drivers if value_driver_id not in
                             [value_driver['id'] for value_driver in value_driver_res]]

        if add_value_drivers:
            add_value_driver_formulas(db_connection, vcs_row_id, design_group_id, add_value_drivers)
        if delete_value_drivers:
            delete_value_driver_formulas(db_connection, vcs_row_id, design_group_id, delete_value_drivers)

        where_statement = "vcs_row = %s and design_group = %s and " \
                          "external_factor IN (" + ",".join(["%s" for _ in range(len(formulas.external_factors))]) + ")"
        select_statement = MySQLStatementBuilder(db_connection)
        external_factor_res = select_statement.select(CVS_FORMULAS_EXTERNAL_FACTORS_TABLE,
                                                      CVS_FORMULAS_EXTERNAL_FACTORS_COLUMNS) \
            .where(where_statement, [vcs_row_id, design_group_id] + formulas.external_factors) \
            .execute(fetch_type=FetchType.FETCH_ALL, dictionary=True)

        delete_external_factors = [external_factor_id['id'] for external_factor_id in external_factor_res if
                                   external_factor_id not in
                                   formulas.external_factors]
        add_external_factors = [external_factor_id for external_factor_id in formulas.value_drivers if
                                external_factor_id not in
                                [external_factor['id'] for external_factor in external_factor_res]]

        if add_external_factors:
            add_external_factor_formulas(db_connection, vcs_row_id, design_group_id, add_external_factors)
        if delete_external_factors:
            delete_external_factor_formulas(db_connection, vcs_row_id, design_group_id, delete_external_factors)


    else:
        raise exceptions.FormulasFailedUpdateException

    return True


def get_all_formulas(db_connection: PooledMySQLConnection, project_id: int, vcs_id: int,
                     design_group_id: int) -> List[models.FormulaGet]:
    logger.debug(f'Fetching all formulas with vcs_id={vcs_id}')

    get_design_group(db_connection, project_id, design_group_id)  # Check if design group exists and matches project
    get_vcs(db_connection, project_id, vcs_id)

    select_statement = MySQLStatementBuilder(db_connection)
    res = select_statement.select(CVS_FORMULAS_TABLE, CVS_FORMULAS_COLUMNS) \
        .inner_join('cvs_vcs_rows', 'vcs_row = cvs_vcs_rows.id') \
        .where('vcs = %s and design_group = %s', [vcs_id, design_group_id]) \
        .execute(fetch_type=FetchType.FETCH_ALL, dictionary=True)

    if res is None:
        raise vcs_exceptions.VCSNotFoundException

    return [populate_formula(r) for r in res]


def populate_formula(db_result) -> models.FormulaGet:
    return models.FormulaGet(
        vcs_row_id=db_result['vcs_row'],
        design_group_id=db_result['design_group'],
        time=db_result['time'],
        time_unit=db_result['time_unit'],
        cost=db_result['cost'],
        revenue=db_result['revenue'],
        rate=db_result['rate']
    )


def delete_formulas(db_connection: PooledMySQLConnection, project_id: int, vcs_row_id: int,
                    design_group_id: int) -> bool:
    logger.debug(f'Deleting formulas with vcs_row_id: {vcs_row_id}')

    get_design_group(db_connection, project_id, design_group_id)  # Check if design group exists and matches project
    # get_cvs_project(project_id)
    get_vcs_row(db_connection, project_id, vcs_row_id)

    delete_statement = MySQLStatementBuilder(db_connection)
    _, rows = delete_statement \
        .delete(CVS_FORMULAS_TABLE) \
        .where('vcs_row = %s and design_group = %s', [vcs_row_id, design_group_id]) \
        .execute(return_affected_rows=True)

    if rows != 1:
        raise exceptions.FormulasFailedDeletionException

    return True


def get_vcs_dg_pairs(db_connection: PooledMySQLConnection, project_id: int) -> List[models.VcsDgPairs]:
    query = "SELECT cvs_vcss.name AS vcs_name, cvs_vcss.id AS vcs_id, cvs_design_groups.name AS design_group_name, " \
            "cvs_design_groups.id AS design_group_id, \
    (SELECT count(*) FROM cvs_vcs_rows WHERE cvs_vcs_rows.vcs = cvs_vcss.id) \
    = ((SELECT (count(*)) FROM cvs_design_mi_formulas INNER JOIN cvs_vcs_rows ON cvs_vcs_rows.id = vcs_row WHERE " \
            "cvs_design_mi_formulas.design_group=cvs_design_groups.id AND vcs=cvs_vcss.id)) \
    AS has_formulas FROM cvs_vcss, cvs_design_groups WHERE cvs_vcss.project = %s AND cvs_design_groups.project = %s \
    GROUP BY vcs_id, design_group_id ORDER BY has_formulas DESC;"

    with db_connection.cursor(prepared=True) as cursor:
        # Log for sanity check
        logger.debug(f"get_vcs_dg_pairs: '{query}'")

        # Execute query
        cursor.execute(query, [project_id, project_id])

        # Get result
        res_dict = []
        rs = cursor.fetchall()
        for res in rs:
            zip(cursor.column_names, res)
            res_dict.append(models.VcsDgPairs(
                vcs=res[0],
                vcs_id=res[1],
                design_group=res[2],
                design_group_id=res[3],
                has_formulas=res[4]
            ))

    return res_dict

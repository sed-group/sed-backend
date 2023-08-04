from typing import List

from fastapi.logger import logger
from mysql.connector.pooling import PooledMySQLConnection
import re
from sedbackend.apps.cvs.design.storage import get_design_group
from sedbackend.apps.cvs.market_input.storage import populate_external_factor
from sedbackend.apps.cvs.vcs.storage import get_vcs_row, populate_value_driver
from sedbackend.apps.cvs.vcs.storage import get_vcs
from sedbackend.apps.cvs.link_design_lifecycle import models, exceptions
from mysqlsb import FetchType, MySQLStatementBuilder

CVS_FORMULAS_TABLE = 'cvs_design_mi_formulas'
CVS_FORMULAS_COLUMNS = ['project', 'vcs_row', 'design_group', 'time', 'time_comment', 'time_unit', 'cost',
                        'cost_comment', 'revenue', 'revenue_comment', 'rate']

CVS_VALUE_DRIVERS_TABLE = 'cvs_value_drivers'
CVS_VALUE_DRIVERS_COLUMNS = ['id', 'user', 'name', 'unit']

CVS_FORMULAS_VALUE_DRIVERS_TABLE = 'cvs_formulas_value_drivers'
CVS_FORMULAS_VALUE_DRIVERS_COLUMNS = ['vcs_row', 'design_group', 'value_driver', 'project']

CVS_FORMULAS_EXTERNAL_FACTORS_TABLE = 'cvs_formulas_external_factors'
CVS_FORMULAS_EXTERNAL_FACTORS_COLUMNS = ['vcs_row', 'design_group', 'external_factor']

CVS_PROJECT_VALUE_DRIVERS_TABLE = 'cvs_project_value_drivers'
CVS_PROJECT_VALUE_DRIVERS_COLUMNS = ['project', 'value_driver']


def create_formulas(db_connection: PooledMySQLConnection, project_id: int, vcs_row_id: int, design_group_id: int,
                    formula_row: models.FormulaRowPost):
    logger.debug(f'Creating formulas')

    value_driver_ids, external_factor_ids = find_vd_and_ef(
        [formula_row.time.formula, formula_row.cost.formula, formula_row.revenue.formula])

    values = [project_id, vcs_row_id, design_group_id, formula_row.time.formula, formula_row.time.comment,
              formula_row.time_unit.value,
              formula_row.cost.formula, formula_row.cost.comment,
              formula_row.revenue.formula, formula_row.revenue.comment, formula_row.rate.value]

    try:
        insert_statement = MySQLStatementBuilder(db_connection)
        insert_statement \
            .insert(table=CVS_FORMULAS_TABLE, columns=CVS_FORMULAS_COLUMNS) \
            .set_values(values=values) \
            .execute(fetch_type=FetchType.FETCH_NONE)
    except Exception as e:
        logger.error(f'Error while inserting formulas: {e}')
        raise exceptions.FormulasFailedUpdateException

    if value_driver_ids:
        add_value_driver_formulas(db_connection, vcs_row_id, design_group_id, value_driver_ids, project_id)
    if external_factor_ids:
        add_external_factor_formulas(db_connection, vcs_row_id, design_group_id, external_factor_ids)


def find_vd_and_ef(texts: List[str]) -> (List[str], List[int]):
    value_driver_ids = []
    external_factor_ids = []

    pattern = r'\{(?P<tag>vd|ef):(?P<id>\d+),"([^"]+)"\}'

    for text in texts:
        matches = re.findall(pattern, text)
        for tag, id_number, _ in matches:
            if tag == "vd":
                value_driver_ids.append(int(id_number))
            elif tag == "ef":
                external_factor_ids.append(int(id_number))

    return value_driver_ids, external_factor_ids


def edit_formulas(db_connection: PooledMySQLConnection, vcs_row_id: int, design_group_id: int, project_id: int,
                  formula_row: models.FormulaRowPost):
    logger.debug(f'Editing formulas')

    value_driver_ids, external_factor_ids = find_vd_and_ef(
        [formula_row.time.formula, formula_row.cost.formula, formula_row.revenue.formula])

    columns = CVS_FORMULAS_COLUMNS[3:]
    set_statement = ', '.join([col + ' = %s' for col in columns])

    values = [formula_row.time.formula, formula_row.time.comment, formula_row.time_unit.value, formula_row.cost.formula,
              formula_row.cost.comment, formula_row.revenue.formula, formula_row.revenue.comment,
              formula_row.rate.value]

    # Update formula row
    update_statement = MySQLStatementBuilder(db_connection)
    _, rows = update_statement \
        .update(table=CVS_FORMULAS_TABLE, set_statement=set_statement, values=values) \
        .where('vcs_row = %s and design_group = %s', [vcs_row_id, design_group_id]) \
        .execute(return_affected_rows=True)

    update_value_driver_formulas(db_connection, vcs_row_id, design_group_id, value_driver_ids, project_id)

    update_external_factor_formulas(db_connection, vcs_row_id, design_group_id, external_factor_ids)


def add_value_driver_formulas(db_connection: PooledMySQLConnection, vcs_row_id: int, design_group_id: int,
                              value_drivers: List[int], project_id: int):

    # Add value driver to project if not already added
    select_statement = MySQLStatementBuilder(db_connection)
    project_value_driver_res = select_statement \
        .select(CVS_PROJECT_VALUE_DRIVERS_TABLE, CVS_PROJECT_VALUE_DRIVERS_COLUMNS) \
        .where(f'project = %s and value_driver in ({",".join(["%s" for _ in range(len(value_drivers))])})',
               [project_id] + value_drivers) \
        .execute(fetch_type=FetchType.FETCH_ALL, dictionary=True)

    value_drivers_outside_project = [vd_id for vd_id in value_drivers if
                                     vd_id not in [res['value_driver'] for res in project_value_driver_res]]

    if value_drivers_outside_project:
        try:
            prepared_list = []
            insert_statement = f'INSERT INTO {CVS_PROJECT_VALUE_DRIVERS_TABLE} (project, value_driver) VALUES'
            for value_driver_id in value_drivers_outside_project:
                insert_statement += f'(%s, %s),'
                prepared_list += [project_id, value_driver_id]
            insert_statement = insert_statement[:-1]
            with db_connection.cursor(prepared=True) as cursor:
                cursor.execute(insert_statement, prepared_list)
        except Exception as e:
            logger.error(f'Error adding value driver to project: {e}')
            raise exceptions.CouldNotAddValueDriverToProjectException

    # Add value driver to formulas
    try:
        prepared_list = []
        insert_statement = f'INSERT INTO {CVS_FORMULAS_VALUE_DRIVERS_TABLE} (vcs_row, design_group, value_driver, project) VALUES'
        for value_driver_id in value_drivers:
            insert_statement += f'(%s, %s, %s, %s),'
            prepared_list += [vcs_row_id, design_group_id, value_driver_id, project_id]
        insert_statement = insert_statement[:-1]
        insert_statement += ' ON DUPLICATE KEY UPDATE vcs_row = vcs_row'  # On duplicate do nothing
        with db_connection.cursor(prepared=True) as cursor:
            cursor.execute(insert_statement, prepared_list)
    except Exception as e:
        logger.error(f'Error while inserting value drivers: {e}')
        raise exceptions.FormulasFailedUpdateException


def delete_value_driver_formulas(db_connection: PooledMySQLConnection, vcs_row_id: int, design_group_id: int,
                                 value_drivers: List[int]):
    delete_statement = MySQLStatementBuilder(db_connection)
    _, rows = delete_statement \
        .delete(CVS_FORMULAS_VALUE_DRIVERS_TABLE) \
        .where(
        f'vcs_row = %s and design_group = %s and value_driver in ({",".join(["%s" for _ in range(len(value_drivers))])})',
        [vcs_row_id, design_group_id] + value_drivers) \
        .execute(return_affected_rows=True)


def update_value_driver_formulas(db_connection: PooledMySQLConnection, vcs_row_id: int, design_group_id: int,
                                 value_drivers: List[int], project_id: int):
    where_statement = "vcs_row = %s and design_group = %s"
    select_statement = MySQLStatementBuilder(db_connection)
    value_driver_res = select_statement.select(CVS_FORMULAS_VALUE_DRIVERS_TABLE, CVS_FORMULAS_VALUE_DRIVERS_COLUMNS) \
        .where(where_statement, [vcs_row_id, design_group_id]) \
        .execute(fetch_type=FetchType.FETCH_ALL, dictionary=True)

    delete_value_drivers = [value_driver['value_driver'] for value_driver in value_driver_res if
                            value_driver['value_driver'] not in
                            value_drivers]
    add_value_drivers = [value_driver_id for value_driver_id in value_drivers if value_driver_id not in
                         [value_driver['value_driver'] for value_driver in value_driver_res]]

    if len(add_value_drivers):
        add_value_driver_formulas(db_connection, vcs_row_id, design_group_id, add_value_drivers, project_id)
    if len(delete_value_drivers):
        delete_value_driver_formulas(db_connection, vcs_row_id, design_group_id, delete_value_drivers)


def add_external_factor_formulas(db_connection: PooledMySQLConnection, vcs_row_id: int, design_group_id: int,
                                 external_factors: List[int]):
    try:
        prepared_list = []
        insert_statement = f'INSERT INTO {CVS_FORMULAS_EXTERNAL_FACTORS_TABLE} (vcs_row, design_group, external_factor) VALUES'
        for external_factor_id in external_factors:
            insert_statement += f'(%s, %s, %s),'
            prepared_list += [vcs_row_id, design_group_id, external_factor_id]
        insert_statement = insert_statement[:-1]
        insert_statement += ' ON DUPLICATE KEY UPDATE vcs_row = vcs_row'  # On duplicate do nothing
        with db_connection.cursor(prepared=True) as cursor:
            cursor.execute(insert_statement, prepared_list)
    except Exception as e:
        logger.error(f'Error while inserting external factors: {e}')
        raise exceptions.FormulasFailedUpdateException


def delete_external_factor_formulas(db_connection: PooledMySQLConnection, vcs_row_id: int, design_group_id: int,
                                    external_factors: List[int]):
    delete_statement = MySQLStatementBuilder(db_connection)
    _, rows = delete_statement \
        .delete(CVS_FORMULAS_EXTERNAL_FACTORS_TABLE) \
        .where(
        f'vcs_row = %s and design_group = %s and external_factor in ({",".join(["%s" for _ in range(len(external_factors))])})',
        [vcs_row_id, design_group_id] + external_factors) \
        .execute(return_affected_rows=True)


def update_external_factor_formulas(db_connection: PooledMySQLConnection, vcs_row_id: int, design_group_id: int,
                                    external_factors: List[int]):
    where_statement = "vcs_row = %s and design_group = %s"
    select_statement = MySQLStatementBuilder(db_connection)
    external_factor_res = select_statement.select(CVS_FORMULAS_EXTERNAL_FACTORS_TABLE,
                                                  CVS_FORMULAS_EXTERNAL_FACTORS_COLUMNS) \
        .where(where_statement, [vcs_row_id, design_group_id]) \
        .execute(fetch_type=FetchType.FETCH_ALL, dictionary=True)

    delete_external_factors = [external_factor['external_factor'] for external_factor in external_factor_res if
                               external_factor['external_factor'] not in
                               external_factors]
    add_external_factors = [external_factor_id for external_factor_id in external_factors if
                            external_factor_id not in
                            [external_factor['external_factor'] for external_factor in external_factor_res]]

    if len(add_external_factors):
        add_external_factor_formulas(db_connection, vcs_row_id, design_group_id, add_external_factors)
    if len(delete_external_factors):
        delete_external_factor_formulas(db_connection, vcs_row_id, design_group_id, delete_external_factors)


def update_formulas(db_connection: PooledMySQLConnection, project_id: int, vcs_row_id: int, design_group_id: int,
                    formula_row: models.FormulaRowPost) -> bool:
    get_design_group(db_connection, project_id, design_group_id)  # Check if design group exists and matches project
    get_vcs_row(db_connection, project_id, vcs_row_id)

    count_statement = MySQLStatementBuilder(db_connection)
    count = count_statement.count(CVS_FORMULAS_TABLE) \
        .where('vcs_row = %s and design_group = %s', [vcs_row_id, design_group_id]) \
        .execute(fetch_type=FetchType.FETCH_ONE, dictionary=True)
    count = count['count']

    if count == 0:
        create_formulas(db_connection, project_id, vcs_row_id, design_group_id, formula_row)
    elif count == 1:
        edit_formulas(db_connection, vcs_row_id, design_group_id, project_id, formula_row)
    else:
        raise exceptions.FormulasFailedUpdateException

    return True


def get_all_formulas(db_connection: PooledMySQLConnection, project_id: int, vcs_id: int,
                     design_group_id: int, user_id: int) -> List[models.FormulaRowGet]:
    logger.debug(f'Fetching all formulas with vcs_id={vcs_id}')

    get_design_group(db_connection, project_id, design_group_id)  # Check if design group exists and matches project
    get_vcs(db_connection, project_id, vcs_id, user_id)

    select_statement = MySQLStatementBuilder(db_connection)
    res = select_statement.select(CVS_FORMULAS_TABLE, CVS_FORMULAS_COLUMNS) \
        .inner_join('cvs_vcs_rows', 'vcs_row = cvs_vcs_rows.id') \
        .where('vcs = %s and design_group = %s', [vcs_id, design_group_id]) \
        .execute(fetch_type=FetchType.FETCH_ALL, dictionary=True)

    if res is None:
        raise exceptions.FormulasNotFoundException

    if len(res):
        where_statement = "(vcs_row, design_group) IN (" + ",".join(["(%s, %s)" for _ in range(len(res))]) + ")"
        prepared_list = []
        for r in res:
            prepared_list += [r['vcs_row'], r['design_group']]

        with db_connection.cursor(prepared=True) as cursor:
            cursor.execute(
                f"SELECT id, name, unit, vcs_row, design_group FROM cvs_formulas_value_drivers "
                f"INNER JOIN cvs_value_drivers ON cvs_formulas_value_drivers.value_driver = cvs_value_drivers.id WHERE {where_statement}",
                prepared_list)
            all_vds = [dict(zip(cursor.column_names, row)) for row in cursor.fetchall()]

        with db_connection.cursor(prepared=True) as cursor:
            cursor.execute(
                f"SELECT id, name, unit, vcs_row, design_group FROM {CVS_FORMULAS_EXTERNAL_FACTORS_TABLE} "
                f"INNER JOIN cvs_market_inputs ON {CVS_FORMULAS_EXTERNAL_FACTORS_TABLE}.external_factor = cvs_market_inputs.id WHERE {where_statement}",
                prepared_list)
            all_efs = [dict(zip(cursor.column_names, row)) for row in cursor.fetchall()]

    formulas = []
    for r in res:
        r['value_drivers'] = [vd for vd in all_vds if vd['vcs_row'] == r['vcs_row'] and
                              vd['design_group'] == r['design_group']]
        r['external_factors'] = [ef for ef in all_efs if ef['vcs_row'] == r['vcs_row'] and
                                 ef['design_group'] == r['design_group']]
        formulas.append(populate_formula(r))

    return formulas


def populate_formula(db_result) -> models.FormulaRowGet:
    return models.FormulaRowGet(
        vcs_row_id=db_result['vcs_row'],
        design_group_id=db_result['design_group'],
        time=models.Formula(formula=db_result['time'], comment=db_result['time_comment']),
        time_unit=db_result['time_unit'],
        cost=models.Formula(formula=db_result['cost'], comment=db_result['cost_comment']),
        revenue=models.Formula(formula=db_result['revenue'], comment=db_result['revenue_comment']),
        rate=db_result['rate'],
        used_value_drivers=[populate_value_driver(valueDriver) for valueDriver in db_result['value_drivers']] if
        db_result['value_drivers'] is not None else [],
        used_external_factors=[populate_external_factor(externalFactor) for externalFactor in
                               db_result['external_factors']] if
        db_result['external_factors'] is not None else [],
    )


def delete_formulas(db_connection: PooledMySQLConnection, project_id: int, vcs_row_id: int,
                    design_group_id: int) -> bool:
    logger.debug(f'Deleting formulas with vcs_row_id: {vcs_row_id}')

    get_design_group(db_connection, project_id, design_group_id)  # Check if design group exists and matches project
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

from typing import List

from fastapi.logger import logger
from mysql.connector.pooling import PooledMySQLConnection

from sedbackend.apps.cvs.design.storage import get_design_group
from sedbackend.apps.cvs.vcs.implementation import get_vcs_row
from sedbackend.apps.cvs.project.implementation import get_cvs_project
from sedbackend.apps.cvs.vcs.implementation import get_vcs
from sedbackend.apps.cvs.link_design_lifecycle import models, exceptions
from sedbackend.libs.mysqlutils.builder import FetchType, MySQLStatementBuilder
from sedbackend.apps.cvs.market_input import implementation as market_impl
from sedbackend.apps.cvs.design import implementation as design_impl


CVS_FORMULAS_TABLE = 'cvs_design_mi_formulas'
CVS_FORMULAS_COLUMNS = ['vcs_row', 'design_group', 'time', 'time_unit', 'cost', 'revenue', 'rate']

CVS_FORMULAS_VALUE_DRIVERS_TABLE = 'cvs_formulas_value_drivers'
CVS_FORMULAS_VALUE_DRIVERS_COLUMNS = ['formulas', 'value_driver']

CVS_FORMULAS_MARKET_INPUTS_TABLE = 'cvs_formulas_market_inputs'
CVS_FORMULAS_MARKET_INPUTS_COLUMNS = ['formulas', 'market_input']


def create_formulas(db_connection: PooledMySQLConnection, vcs_row_id: int, design_group_id: int,
                    formulas: models.FormulaPost) -> bool:
    logger.debug(f'Creating formulas')

    values = [vcs_row_id, design_group_id, formulas.time, formulas.time_unit.value, formulas.cost, formulas.revenue,
              formulas.rate.value]

    insert_statement = MySQLStatementBuilder(db_connection)
    insert_statement \
        .insert(table=CVS_FORMULAS_TABLE, columns=CVS_FORMULAS_COLUMNS) \
        .set_values(values=values) \
        .execute(fetch_type=FetchType.FETCH_ONE)

    if formulas.value_driver_ids is not None:
        for vd in formulas.value_driver_ids:
            insert_statement = MySQLStatementBuilder(db_connection)
            insert_statement \
                .insert(table=CVS_FORMULAS_VALUE_DRIVERS_TABLE, columns=CVS_FORMULAS_VALUE_DRIVERS_COLUMNS) \
                .set_values([vcs_row_id, vd]) \
                .execute(fetch_type=FetchType.FETCH_NONE)

    if formulas.market_input_ids is not None:
        for mi_id in formulas.market_input_ids:
            insert_statement = MySQLStatementBuilder(db_connection)
            insert_statement \
                .insert(table=CVS_FORMULAS_MARKET_INPUTS_TABLE, columns=CVS_FORMULAS_MARKET_INPUTS_COLUMNS) \
                .set_values([vcs_row_id, mi_id]) \
                .execute(fetch_type=FetchType.FETCH_NONE)

    if insert_statement is not None:  # TODO actually check for potential problems
        return True
    
    return False


def edit_formulas(db_connection: PooledMySQLConnection, project_id: int, vcs_row_id: int, design_group_id: int,
                  formulas: models.FormulaPost) -> bool:

    get_design_group(db_connection, project_id, design_group_id)  # Check if design group exists and matches project
    get_vcs_row(vcs_row_id)

    count_statement = MySQLStatementBuilder(db_connection)
    count = count_statement.count(CVS_FORMULAS_TABLE)\
        .where('vcs_row = %s and design_group = %s', [vcs_row_id, design_group_id])\
        .execute(fetch_type=FetchType.FETCH_ONE, dictionary=True)
    count = count['count']

    logger.debug(f'count: {count}')

    if count == 0:
        create_formulas(db_connection,  vcs_row_id, design_group_id, formulas)
    elif count == 1:
        logger.debug(f'Editing formulas')
        columns = CVS_FORMULAS_COLUMNS[2:]
        set_statement = ', '.join([col + ' = %s' for col in columns])

        values = [formulas.time, formulas.time_unit.value, formulas.cost, formulas.revenue, formulas.rate.value]

        # TODO update the connection with value drivers and mi also
        update_statement = MySQLStatementBuilder(db_connection)
        _, rows = update_statement \
            .update(table=CVS_FORMULAS_TABLE, set_statement=set_statement, values=values) \
            .where('vcs_row = %s and design_group = %s', [vcs_row_id, design_group_id])\
            .execute(return_affected_rows=True)
    
        if rows > 1:
            raise exceptions.TooManyFormulasUpdatedException
    else:
        raise exceptions.FormulasFailedUpdateException
    
    return True


def get_all_formulas(db_connection: PooledMySQLConnection, project_id: int, vcs_id: int,
                     design_group_id: int) -> List[models.FormulaRowGet]:
    logger.debug(f'Fetching all formulas with vcs_id={vcs_id}')

    get_design_group(db_connection, project_id, design_group_id)  # Check if design group exists and matches project
    get_cvs_project(project_id)
    get_vcs(vcs_id, project_id)

    select_statement = MySQLStatementBuilder(db_connection)
    res = select_statement.select(CVS_FORMULAS_TABLE, CVS_FORMULAS_COLUMNS) \
        .inner_join('cvs_vcs_rows', 'vcs_row = cvs_vcs_rows.id') \
        .where('vcs = %s and design_group = %s', [vcs_id, design_group_id]) \
        .execute(fetch_type=FetchType.FETCH_ALL, dictionary=True)
    
    if res is None:
        raise exceptions.VCSNotFoundException
    
    return [populate_formula(r) for r in res]


def populate_formula(db_result) -> models.FormulaRowGet:
    return models.FormulaRowGet(
        vcs_row_id=db_result['vcs_row'],
        design_group_id=db_result['design_group'],
        time=db_result['time'],
        time_unit=db_result['time_unit'],
        cost=db_result['cost'],
        revenue=db_result['revenue'],
        rate=db_result['rate'],
        market_inputs=market_impl.get_all_formula_market_inputs(db_result['vcs_row']),
        value_drivers=design_impl.get_all_formula_value_drivers(db_result['vcs_row'])
    )


def delete_formulas(db_connection: PooledMySQLConnection, project_id: int, vcs_row_id: int,
                    design_group_id: int) -> bool:
    logger.debug(f'Deleting formulas with vcs_row_id: {vcs_row_id}')

    get_design_group(db_connection, project_id, design_group_id)  # Check if design group exists and matches project
    #get_cvs_project(project_id)
    get_vcs_row(vcs_row_id)


    delete_statement = MySQLStatementBuilder(db_connection)
    _, rows = delete_statement \
        .delete(CVS_FORMULAS_TABLE) \
        .where('vcs_row = %s and design_group = %s', [vcs_row_id, design_group_id])\
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

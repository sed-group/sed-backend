from multiprocessing import Pool
from operator import truediv
from time import time
from typing import List

from fastapi.logger import logger
from mysql.connector.pooling import PooledMySQLConnection
from sedbackend.apps.cvs.design.models import QuantifiedObjective

from sedbackend.apps.cvs.link_design_lifecycle import models, exceptions
from sedbackend.libs.mysqlutils.builder import FetchType, MySQLStatementBuilder
from sedbackend.apps.cvs.market_input import implementation as market_impl
from sedbackend.apps.cvs.design import implementation as design_impl


CVS_FORMULAS_TABLE = 'cvs_design_mi_formulas'
CVS_FORMULAS_COLUMNS = ['vcs_row', 'time', 'time_unit', 'cost', 'revenue', 'rate']

CVS_FORMULAS_QUANTIFIED_OBJECTIVES_TABLE = 'cvs_formulas_quantified_objectives'
CVS_FORMULAS_QUANTIFIED_OBJECTIVES_COLUMNS = ['formulas', 'value_driver', 'design_group']

CVS_FORMULAS_MARKET_INPUTS_TABLE = 'cvs_formulas_market_inputs'
CVS_FORMULAS_MARKET_INPUTS_COLUMNS = ['formulas', 'market_input']

def create_formulas(db_connection: PooledMySQLConnection, vcs_row_id: int, formulas: models.FormulaPost) -> bool:
    logger.debug(f'Creating formulas')

    values = [vcs_row_id, formulas.time, formulas.time_unit, formulas.cost, formulas.revenue, formulas.rate]

    insert_statement = MySQLStatementBuilder(db_connection)
    insert_statement \
        .insert(table=CVS_FORMULAS_TABLE, columns=CVS_FORMULAS_COLUMNS) \
        .set_values(values=values) \
        .execute(fetch_type=FetchType.FETCH_ONE)
    
    for qo in formulas.quantified_objective_ids:
        insert_statement \
            .insert(table=CVS_FORMULAS_QUANTIFIED_OBJECTIVES_TABLE, columns=CVS_FORMULAS_QUANTIFIED_OBJECTIVES_COLUMNS) \
            .set_values([vcs_row_id, qo.value_driver_id, qo.design_group_id]) \
            .execute(fetch_type=FetchType.FETCH_NONE)

    for mi_id in formulas.market_input_ids:
        insert_statement \
            .insert(table=CVS_FORMULAS_MARKET_INPUTS_TABLE, columns=CVS_FORMULAS_MARKET_INPUTS_COLUMNS) \
            .set_values([vcs_row_id, mi_id]) \
            .execute(fetch_type=FetchType.FETCH_NONE)

    if insert_statement is not None:
        return True
    
    return False

def edit_formulas(db_connection: PooledMySQLConnection, vcs_row_id: int, formulas: models.FormulaPost) -> bool:
    logger.debug(f'Editing formulas')

    columns = CVS_FORMULAS_COLUMNS[1:]
    set_statement = ', '.join([col + ' = %s' for col in columns])

    values = [formulas.time, formulas.time_unit, formulas.cost, formulas.revenue, formulas.rate]

    update_statement = MySQLStatementBuilder(db_connection)
    res = update_statement \
        .update(table=CVS_FORMULAS_TABLE, set_statement=set_statement, values=values) \
        .where('vcs_row = %s', [vcs_row_id])\
        .execute(fetch_type=FetchType.FETCH_ALL, dictionary=False)
    
    if res is None:
        raise exceptions.FormulasFailedUpdateException
    
    return True


def get_all_formulas(db_connection: PooledMySQLConnection, vcs_id: int) -> List[models.FormulaRowGet]:
    logger.debug(f'Fetching all formulas with vcs_id={vcs_id}')

    select_statement = MySQLStatementBuilder(db_connection)
    res = select_statement.select(CVS_FORMULAS_TABLE, CVS_FORMULAS_COLUMNS) \
        .inner_join('cvs_vcs_rows', 'vcs_row = cvs_vcs_rows.id') \
        .where('vcs = %s', [vcs_id]) \
        .execute(fetch_type=FetchType.FETCH_ALL, dictionary=True)
    
    if res is None:
        raise exceptions.VCSNotFoundException
    
    return [populate_formula(r) for r in res]

def populate_formula(db_result) -> models.FormulaRowGet:
    return models.FormulaRowGet(
        vcs_row_id=db_result['vcs_row'],
        time=db_result['time'],
        time_unit=db_result['time_unit'],
        cost=db_result['cost'],
        revenue=db_result['revenue'],
        rate=db_result['rate'],
        quantified_objectives=design_impl.get_all_formula_quantified_objectives(db_result['vcs_row']),
        market_inputs=market_impl.get_all_formula_market_inputs(db_result['vcs_row'])
    )

def delete_formulas(db_connection: PooledMySQLConnection, vcs_row_id: int) -> bool:
    logger.debug(f'Deleting formulas with vcs_row_id: {vcs_row_id}')

    delete_statement = MySQLStatementBuilder(db_connection)
    rows,_ = delete_statement \
        .delete(CVS_FORMULAS_TABLE) \
        .where('vcs_row = %s', [vcs_row_id])\
        .execute(fetch_type=FetchType.FETCH_ALL)
    
    if len(rows) != 1:
        raise exceptions.FormulasFailedDeletionException
    
    return True

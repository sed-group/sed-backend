from operator import truediv
from typing import List

from fastapi.logger import logger
from mysql.connector.pooling import PooledMySQLConnection

from sedbackend.apps.cvs.link_design_lifecycle import models
from sedbackend.libs.mysqlutils.builder import FetchType, MySQLStatementBuilder


CVS_FORMULAS_TABLE = 'cvs_design_mi_formulas'
CVS_FORMULAS_COLUMNS = ['vcs_row', 'time', 'time_unit', 'cost', 'revenue']

def create_formulas(db_connection: PooledMySQLConnection, vcs_row_id: int, formulas: models.FormulaPost) -> bool:
    logger.debug(f'Creating formulas')

    values = [vcs_row_id, formulas.time, formulas.time_unit, formulas.cost, formulas.revenue]

    insert_statement = MySQLStatementBuilder(db_connection)
    insert_statement \
        .insert(table=CVS_FORMULAS_TABLE, columns=CVS_FORMULAS_COLUMNS) \
        .set_values(values=values) \
        .execute(fetch_type=FetchType.FETCH_ONE)
    
    if insert_statement is not None:
        return True
    
    return False
from typing import List
from fastapi.logger import logger

from libs.mysqlutils import MySQLStatementBuilder, FetchType


def db_create_product(connection, name: str, design_parameters: dict):
    logger.debug(f'Inserting new product "{name}" with {len(design_parameters)} parameters')
    insert_project_stmnt = MySQLStatementBuilder(connection)
    insert_project_stmnt\
        .insert('products', ['name'])\
        .set_values([name])\
        .execute(return_affected_rows=True)
    product_id = insert_project_stmnt.last_insert_id

    insert_design_parameters_stmnt = MySQLStatementBuilder(connection)
    for dp_name in design_parameters:
        dp_type = design_parameters[dp_name].type
        dp_value = str(design_parameters[dp_name].value)
        logger.debug(f'{dp_name} = {dp_value} [{dp_type}]')

        insert_design_parameters_stmnt\
            .insert('products_design_parameters', ['name', 'value', 'type', 'product_id'])\
            .set_values([dp_name, dp_value, dp_type, product_id])\
            .execute()


def parse_design_parameter_value(value, type):
    pass

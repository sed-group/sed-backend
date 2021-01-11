from .statements import create_prepared_insert_statement
from typing import Tuple, Any
from fastapi.logger import logger


class MySQLStatementBuilder:

    def __init__(self, connection):
        self.con = connection
        self.query = ""
        self.values = None

    def insert(self, table: str, columns: Tuple[str, ...], values: Tuple[Any, ...]):
        self.query = create_prepared_insert_statement(table, columns)
        self.values = values
        return self

    def execute(self):
        logger.debug(f'executing query "{self.query} with values "{self.values}"')
        with self.con.cursor(prepared=True) as cursor:
            cursor.execute(self.query, self.values)
            return None

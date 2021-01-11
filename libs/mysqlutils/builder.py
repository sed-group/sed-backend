from .statements import create_prepared_insert_statement, create_select_statement, create_prepared_where_statement
from typing import Any, List, Optional
from fastapi.logger import logger
from enum import Enum


class FetchType(Enum):
    FETCH_ONE = 1
    FETCH_MANY = 2
    FETCH_ALL = 3
    FETCH_NONE = 4


class MySQLStatementBuilder:

    def __init__(self, connection):
        self.con = connection
        self.query = ""
        self.values = []

    def insert(self, table: str, columns: List[str], values: List[Any]):
        self.query = create_prepared_insert_statement(table, columns)
        self.values.extend(values)
        return self

    def select(self, table: str, columns: List[str]):
        self.query += create_select_statement(table, columns)
        return self

    def where(self, condition, condition_values: List[Any]):
        self.query += create_prepared_where_statement(condition)
        self.values.extend(condition_values)
        return self

    def execute(self, fetch_type: FetchType, size: Optional[int] = None):
        logger.debug(f'executing query "{self.query}" with values "{self.values}"')
        with self.con.cursor(prepared=True) as cursor:
            cursor.execute(self.query, self.values)
            if fetch_type is FetchType.FETCH_ONE:
                return cursor.fetchone()
            if fetch_type is FetchType.FETCH_ALL:
                return cursor.fetchall()
            if fetch_type is FetchType.FETCH_MANY:
                if fetch_type is None:
                    raise ValueError('When using FETCH_MANY size needs to be 1 or higher')
                return cursor.fetchmany(size=size)

            return None



from .statements import *
from typing import Any, List
from fastapi.logger import logger
from enum import Enum


class FetchType(Enum):
    """
    Used to determine how many rows should be fetched by a MySQL statement/query
    """

    FETCH_ONE = "Fetch_One"
    FETCH_MANY = "Fetch_Many"
    FETCH_ALL = "Fetch_All"
    FETCH_NONE = "Fetch_None"


class MySQLStatementBuilder:
    """
    Assists in building simple MySQL queries and statements. Does not need to be closed.
    It automatically closes the MySQL cursor.
    """

    def __init__(self, connection):
        self.con = connection
        self.query = ""
        self.values = []

    def insert(self, table: str, columns: List[str]):
        """
        Create a prepared insert statement

        :param table:
        :param columns:
        :return:
        """
        self.query += create_insert_statement(table, columns)
        return self

    def set_values(self, values):
        print('values')
        self.query += create_prepared_values_statement(len(values))
        self.values.extend(values)
        return self

    def select(self, table: str, columns: List[str]):
        """
        Create a select statement

        :param table:
        :param columns:
        :return:
        """

        self.query += create_select_statement(table, columns)
        return self

    def delete(self, table: str):
        self.query += create_delete_statement(table)
        return self

    def order_by(self, columns: List[str], order: Sort = None):
        self.query += create_order_by_statement(columns, order)
        return self

    def offset(self, offset_count: int):
        self.query += create_offset_statement(offset_count)
        return self

    def limit(self, limit_count: int):
        self.query += create_limit_statement(limit_count)
        return self

    def where(self, condition, condition_values: List[Any]):
        """
        Create prepared WHERE statement
        :param condition: Should be a prepared condition. Use %s or ? to represent variables
        :param condition_values: List of condition variables (switches out the %s and ? prepared placeholders)
        :return:
        """

        self.query += create_prepared_where_statement(condition)
        self.values.extend(condition_values)
        return self

    def execute(self, fetch_type: FetchType = FetchType.FETCH_NONE, size: int = None, dictionary: bool = False):
        """
        Executes constructed MySQL query. Does not need to be closed (closes automatically).

        :param dictionary: boolean. Default is False. Converts response to dictionaries
        :param fetch_type: FetchType.FETCH_NONE by default
        :param size: Required when using FetchType.FETCH_MANY. Determines how many rows to fetch
        :return: None by default, but can be changed by seting keyword param "fetch_type"
        """

        logger.debug(f'executing query "{self.query}" with values "{self.values}". fetch_type={fetch_type}')

        with self.con.cursor(prepared=True) as cursor:
            cursor.execute(self.query, self.values)

            # Determine what the query should return
            if fetch_type is FetchType.FETCH_ONE:
                res = cursor.fetchone()
            elif fetch_type is FetchType.FETCH_ALL:
                res = cursor.fetchall()
            elif fetch_type is FetchType.FETCH_MANY:
                if size is None:
                    raise ValueError('When using FETCH_MANY size needs to be 1 or higher')
                res = cursor.fetchmany(size=size)
            elif fetch_type is FetchType.FETCH_NONE:
                res = None
            else:
                res = None

            # Convert result to dictionary (or, array of dictionaries) if requested
            if dictionary is True:

                if res is None:
                    return res

                if fetch_type in [FetchType.FETCH_ALL, FetchType.FETCH_MANY]:
                    dict_array = []
                    for row in res:
                        dict_array.append(dict(zip(cursor.column_names, row)))

                    res = dict_array

                elif fetch_type is FetchType.FETCH_ONE:
                    res = dict(zip(cursor.column_names, res))

            return res

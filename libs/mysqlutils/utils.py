from typing import List, Any, TypeVar

from mysql.connector.pooling import PooledMySQLConnection

from libs.mysqlutils.builder import MySQLStatementBuilder, FetchType


def delete_by_id(connection: PooledMySQLConnection, table: str, id: int):
    res, rows = MySQLStatementBuilder(connection).delete(table)\
        .where("id = ?", [id])\
        .execute(fetch_type=FetchType.FETCH_NONE, return_affected_rows=True)

    if rows == 0:
        raise Exception

    return True


def get_by_id(connection: PooledMySQLConnection, table: str, db_id: int, T: Any):
    res = MySQLStatementBuilder(connection)\
        .select_all(table)\
        .where("id = ?", [db_id])\
        .execute(dictionary=True, fetch_type=FetchType.FETCH_ALL)

    if res is None:
        raise Exception

    return T(**res)


def get_all_with(connection: PooledMySQLConnection, table: str, prepared_where_stmnt: str, cols: List[str], T: Any):
    rs = MySQLStatementBuilder(connection)\
        .select_all(table)\
        .where(prepared_where_stmnt, cols)\
        .execute(fetch_type=FetchType.FETCH_ALL, dictionary=True)

    # TODO: Raise..

    results_array = []
    for res in rs:
        results_array.append(T(**res))

    return results_array


def exclude_cols(column_list: List[str], exclude_list: List[str]):
    """
    Takes a list of strings, and excludes all entries in the exlclude list.
    Returns a copy of the list, but without the excluded entries.
    Does not change the inserted list.
    :return:
    """
    column_list_copy = column_list[:]

    for exclude_col in exclude_list:
        if exclude_col in column_list:
            column_list_copy.remove(exclude_col)
        else:
            raise ValueError("Excluded column could not be found in column list.")

    return column_list_copy

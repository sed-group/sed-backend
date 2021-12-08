from typing import List
from enum import Enum


class Sort(Enum):
    ASCENDING = 'ASC'
    DESCENDING = 'DESC'


def create_insert_statement(table: str, columns: List[str], backticks=True):

    if backticks:
        insert_cols_str = ', '.join(wrap_in_backticks(columns))                 # `col1`, `col2`, `col3`, ..
    else:
        insert_cols_str = ', '.join(columns)                                    # col1, col2, col3, ..

    query = f"INSERT INTO {table} ({insert_cols_str}) "
    return query


def create_select_statement(table, columns: List[str]):
    return f"SELECT {','.join(wrap_in_backticks(columns))} FROM {table} "   # SELECT col1, col2 FROM table


def create_select_all_statement(table):
    return f"SELECT * FROM {table} "   # SELECT col1, col2 FROM table


def create_count_statement(table):
    return f"SELECT COUNT(*) as count FROM {table} "


def create_delete_statement(table: str):
    return f"DELETE FROM {table} "


def create_update_statement(table: str, set_statement: str):
    return f"UPDATE {table} SET {set_statement} "


def create_prepared_values_statement(count: int):
    placeholder_array = ['%s'] * count
    placeholder_str = ', '.join(placeholder_array)
    return f"VALUES ({placeholder_str}) "


def create_prepared_where_statement(condition):
    return f"WHERE {condition} "


def create_limit_statement(n):
    return f"LIMIT {n} "


def create_offset_statement(n):
    return f"OFFSET {n} "


def create_order_by_statement(columns: List[str], order: Sort = None):
    cols_str = ', '.join(wrap_in_backticks(columns))
    if order:
        return f"ORDER BY {cols_str} {order.value} "
    else:
        return f"ORDER BY {cols_str} "


def create_inner_join_statement(target_table, join_statement):
    return f"INNER JOIN {target_table} ON {join_statement} "


def wrap_in_backticks(array: List[str]):
    """
    Wraps each element in back-ticks. This is useful for escaping reserved key-words,
    and future-proofing column/table names.
    :param array: Array of table/column names
    :return:
    """
    new_array = []
    for element in array:
        element = element.replace('.', '`.`')
        new_array.append("`{}`".format(element))

    return new_array

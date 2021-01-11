from typing import List


def create_prepared_insert_statement(table: str, columns: List[str]):
    insert_cols_str = ', '.join(wrap_in_backticks(columns))                 # `col1`, `col2`, `col3`, ..
    values_placeholder = ', '.join(['%s'] * len(columns))                   # %s, %s, %s, ..
    query = f"INSERT INTO {table} ({insert_cols_str}) VALUES ({values_placeholder})"
    return query


def create_select_statement(table, columns: List[str]):
    return f"SELECT {','.join(wrap_in_backticks(columns))} FROM {table} "   # SELECT col1, col2 FROM table


def create_prepared_where_statement(condition):
    return f"WHERE {condition}"


def wrap_in_backticks(array: List[str]):
    """
    Wraps each element in back-ticks. This is useful for escaping reserved key-words,
    and future-proofing column/table names.
    :param array: Array of table/column names
    :return:
    """
    new_array = []
    for element in array:
        new_array.append("`{}`".format(element))

    return new_array

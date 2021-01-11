from typing import Tuple


def create_prepared_insert_statement(table: str, columns: Tuple[str, ...]):
    insert_cols_str = '`'+'`, `'.join(columns)+'`'                  # `col1`, `col2`, `col3`, ..
    values_placeholder = ', '.join(['%s'] * len(columns))           # %s, %s, %s, ..
    query = f"INSERT INTO {table} ({insert_cols_str}) VALUES ({values_placeholder})"
    return query

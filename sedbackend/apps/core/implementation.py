import sedbackend.apps.core.storage as storage
from sedbackend.apps.core.db import get_connection


def impl_check_db_connection() -> int:
    with get_connection() as con:
        return storage.db_check_db_connection(con)

from fastapi import HTTPException, status

import apps.core.storage as storage
from apps.core.db import get_connection


def impl_check_db_connection() -> int:
    with get_connection() as con:
        return storage.db_check_db_connection(con)

from fastapi import HTTPException, status

import apps.difam.storage as storage
from apps.core.db import get_connection


def impl_get_difam_projects(segment_length: int, index: int, current_user_id:int):
    with get_connection() as con:
        return storage.db_get_difam_projects(con, segment_length, index, current_user_id)
from fastapi import HTTPException, status

import apps.difam.storage as storage
import apps.difam.models as models
from apps.core.db import get_connection


def impl_get_difam_projects(segment_length: int, index: int, current_user_id:int):
    with get_connection() as con:
        return storage.db_get_difam_projects(con, segment_length, index, current_user_id)


def impl_post_difam_project(difam_project: models.DifamProjectPost, current_user_id: int):
    with get_connection() as con:
        res = storage.db_post_difam_project(con, difam_project, current_user_id)
        con.commit()
        return res


def impl_get_difam_project(difam_project_id: int):
    with get_connection() as con:
        return storage.db_get_difam_project(con, difam_project_id)

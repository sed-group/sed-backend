from fastapi import HTTPException, status

from apps.core.applications.exceptions import ApplicationNotUniqueException, ApplicationNotFoundException
from apps.core.applications.storage import (db_get_applications, db_insert_application, db_get_application,
                                            db_delete_application)
from apps.core.db import get_connection
from apps.core.applications.models import Application


def impl_get_apps(segment_length: int, index: int):
    with get_connection() as con:
        return db_get_applications(con, segment_length, index)


def impl_post_app(app: Application):
    try:
        with get_connection() as con:
            res = db_insert_application(con, app)
            if res:
                con.commit()
    except ApplicationNotUniqueException:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Application is not unique",
        )


def impl_get_app(app_id: int):
    try:
        with get_connection() as con:
            return db_get_application(con, app_id)
    except ApplicationNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No application with ID = {app_id} could be found."
        )


def impl_delete_app(app_id: int):
    try:
        with get_connection() as con:
            res = db_delete_application(con, app_id)
            if res:
                con.commit()
    except ApplicationNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No application with ID = {app_id} could be found."
        )

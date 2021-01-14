from apps.core.applications.storage import (db_get_applications, db_insert_application, db_get_application,
                                            db_delete_application)
from apps.core.db import get_connection
from apps.core.applications.models import Application


def impl_get_apps(segment_length: int, index: int):
    with get_connection() as con:
        return db_get_applications(con, segment_length, index)


def impl_post_app(app: Application):
    with get_connection() as con:
        return db_insert_application(con, app)


def impl_get_app(app_id: int):
    with get_connection() as con:
        return db_get_application(con, app_id)


def impl_delete_app(app_id: int):
    with get_connection() as con:
        return db_delete_application(con, app_id)
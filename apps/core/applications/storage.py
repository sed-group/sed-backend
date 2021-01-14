from typing import List

from libs.mysqlutils import MySQLStatementBuilder, FetchType

from apps.core.applications.models import Application


def db_get_applications(connection, segment_length: int, index: int) -> List[Application]:
    try:
        int(segment_length)
        int(index)
        if index < 0:
            index = 0
    except ValueError:
        raise TypeError

    cols = ['id', 'name', 'href', 'description', 'contact', 'href_access', 'href_docs', 'href_source', 'href_api']
    mysql_statement = MySQLStatementBuilder(connection)
    apps = mysql_statement \
        .select('applications', cols) \
        .limit(segment_length) \
        .offset(segment_length * index) \
        .execute(fetch_type=FetchType.FETCH_ALL, dictionary=True)

    return apps


def db_insert_application(connection, application: Application):
    pass


def db_get_application(con, app_id: int):
    pass


def db_delete_application(con, app_id: int):
    pass

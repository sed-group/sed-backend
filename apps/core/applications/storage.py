from typing import List

from apps.core.applications.exceptions import ApplicationNotUniqueException, ApplicationNotFoundException
from libs.mysqlutils import MySQLStatementBuilder, FetchType
from mysql.connector.errors import IntegrityError

from apps.core.applications.models import Application


TABLE_COLUMNS = ['id', 'name', 'href', 'description', 'contact', 'href_access', 'href_docs', 'href_source', 'href_api']


def db_get_applications(connection, segment_length: int, index: int) -> List[Application]:
    try:
        int(segment_length)
        int(index)
        if index < 0:
            index = 0
        if segment_length < 1:
            segment_length = 1
    except ValueError:
        raise TypeError

    mysql_statement = MySQLStatementBuilder(connection)
    apps = mysql_statement \
        .select('applications', TABLE_COLUMNS) \
        .limit(segment_length) \
        .offset(segment_length * index) \
        .execute(fetch_type=FetchType.FETCH_ALL, dictionary=True)

    return apps


def db_insert_application(connection, application: Application):
    try:
        app = application
        mysql_statement = MySQLStatementBuilder(connection)

        cols = ['name',
                'description',
                'contact',
                'href',
                'href_access',
                'href_docs',
                'href_source',
                'href_api']

        values = [app.name,
                  app.description,
                  app.contact,
                  app.href,
                  app.href_access,
                  app.href_docs,
                  app.href_source,
                  app.href_api]

        mysql_statement.insert('applications', cols).set_values(values).execute()
    except IntegrityError:
        raise ApplicationNotUniqueException

    return True


def db_get_application(connection, app_id: int):
    mysql_statement = MySQLStatementBuilder(connection)
    res = mysql_statement\
        .select("applications", TABLE_COLUMNS)\
        .where("id = %s", [app_id])\
        .execute(FetchType.FETCH_ONE, dictionary=True)

    if res is None:
        raise ApplicationNotFoundException

    return Application(**res)


def db_delete_application(connection, app_id: int):
    mysql_statement = MySQLStatementBuilder(connection)
    res, rows = mysql_statement.delete('applications').where("id = %s", [app_id]).execute(return_affected_rows=True)

    if rows == 0:
        raise ApplicationNotFoundException

    return True

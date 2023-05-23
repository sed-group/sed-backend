from typing import List
from fastapi.logger import logger
from mysql.connector.pooling import PooledMySQLConnection

import sedbackend.apps.core.users.exceptions as exc
import sedbackend.apps.core.users.models as models
from sedbackend.apps.core.authentication.utils import get_password_hash
from mysqlsb import MySQLStatementBuilder, FetchType
from mysql.connector.errors import Error as SQLError

USERS_COLUMNS_SAFE = ['id', 'username', 'email', 'full_name', 'scopes', 'disabled'] # Safe, as it does not contain passwords
USERS_TABLE = 'users'


def db_get_user_safe_with_username(connection: PooledMySQLConnection, user_name: str) -> models.User:
    mysql_statement = MySQLStatementBuilder(connection)
    cols = ['id', 'username', 'email', 'full_name']
    user_data = mysql_statement\
        .select(USERS_TABLE, cols)\
        .where('username = ?', [user_name])\
        .execute(fetch_type=FetchType.FETCH_ONE, dictionary=True)

    if user_data is None:
        raise exc.UserNotFoundException

    user = models.User(**user_data)
    return user


def db_get_user_safe_with_id(connection: PooledMySQLConnection, user_id: int) -> models.User:
    try:
        int(user_id)
    except ValueError:
        raise TypeError

    mysql_statement = MySQLStatementBuilder(connection)
    user_data = mysql_statement\
        .select(USERS_TABLE, USERS_COLUMNS_SAFE)\
        .where('id = %s', [user_id])\
        .execute(fetch_type=FetchType.FETCH_ONE, dictionary=True)

    if user_data is None:
        raise exc.UserNotFoundException

    user = models.User(**user_data)
    return user


def db_get_user_list(connection: PooledMySQLConnection, segment_length: int, index: int) -> List[models.User]:
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
    rs = mysql_statement\
        .select(USERS_TABLE, USERS_COLUMNS_SAFE)\
        .limit(segment_length)\
        .offset(segment_length * index)\
        .execute(fetch_type=FetchType.FETCH_ALL, dictionary=True)

    users = []
    if rs is None:
        return users

    for res in rs:
        user = models.User(**res)
        users.append(user)

    return users


def db_get_users_with_ids(connection: PooledMySQLConnection, user_ids) -> List[models.User]:
    id_set = set(user_ids)

    mysql_statement = MySQLStatementBuilder(connection)
    rs = mysql_statement\
        .select(USERS_TABLE, USERS_COLUMNS_SAFE)\
        .where(f'id IN {MySQLStatementBuilder.placeholder_array(len(user_ids))}', user_ids)\
        .execute(fetch_type=FetchType.FETCH_ALL, dictionary=True)

    users = []

    if rs is None:
        return users

    for res in rs:
        user = models.User(**res)
        users.append(user)
        id_set.remove(user.id)

    if len(id_set) != 0:
        raise exc.UserNotFoundException('The following users could not be found: ' + str(id_set))

    return users


def db_insert_user(connection: PooledMySQLConnection, user: models.UserPost) -> models.User:
    try:
        mysql_statement = MySQLStatementBuilder(connection)

        cols = ['username',
                'password',
                'email',
                'full_name',
                'scopes',
                'disabled']

        vals = [user.username,
                get_password_hash(user.password),
                user.email,
                user.full_name,
                user.scopes,
                user.disabled]

        mysql_statement.insert(USERS_TABLE, cols).set_values(vals).execute(fetch_type=FetchType.FETCH_NONE)
        user_id = mysql_statement.last_insert_id

        return db_get_user_safe_with_id(connection, user_id)

    except SQLError as err:
        logger.error(err)
        raise exc.UserNotUniqueException('Suggested user is not unique.')


def db_delete_user(connection: PooledMySQLConnection, user_id: int) -> bool:

    where_stmnt = 'id = %s'

    user = db_get_user_safe_with_id(connection, user_id)

    if user is None:
        raise exc.UserNotFoundException

    del_stmnt = MySQLStatementBuilder(connection)
    del_stmnt.delete(USERS_TABLE).where(where_stmnt, [user_id]).execute()

    return True


def db_update_user_password(connection: PooledMySQLConnection, user_id: int, new_password: str) -> bool:
    hashed_pwd = get_password_hash(new_password)
    mysql_stmnt = MySQLStatementBuilder(connection)
    res, rows = mysql_stmnt.update('users', 'password = ?', [hashed_pwd])\
        .where("id = ?", [user_id])\
        .execute(fetch_type=FetchType.FETCH_NONE, return_affected_rows=True, no_logs=True)

    if rows == 0:
        raise exc.UserNotFoundException

    return True


def db_update_user_details(connection: PooledMySQLConnection, user_id: int,
                           update_details_request: models.UpdateDetailsRequest):
    stmnt = MySQLStatementBuilder(connection)
    res, rows = stmnt\
        .update('users', 'full_name = ?, email = ?', [update_details_request.full_name, update_details_request.email])\
        .where('id = ?', [user_id])\
        .execute(fetch_type=FetchType.FETCH_NONE, return_affected_rows=True)

    if rows == 0:
        raise exc.UserNotFoundException

    return True

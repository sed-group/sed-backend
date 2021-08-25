from typing import List

from .exceptions import UserNotFoundException, UserNotUniqueException
import apps.core.users.models as models
from apps.core.authentication.utils import get_password_hash, parse_scopes
from apps.core.authentication.exceptions import UnauthorizedOperationException
from libs.mysqlutils import MySQLStatementBuilder, FetchType
from mysql.connector.errors import IntegrityError

USERS_COLUMNS_SAFE = ['id', 'username', 'email', 'full_name', 'scopes', 'disabled'] # Safe, as it does not contain passwords
USERS_TABLE = 'users'


def db_get_user_safe_with_username(connection, user_name: str) -> models.User:
    mysql_statement = MySQLStatementBuilder(connection)
    cols = ['id', 'username', 'email', 'full_name']
    user_data = mysql_statement\
        .select(USERS_TABLE, cols)\
        .where('username = %s', [user_name])\
        .execute(fetch_type=FetchType.FETCH_ONE, dictionary=True)

    if user_data is None:
        raise UserNotFoundException

    user = models.User(**user_data)
    return user


def db_get_user_safe_with_id(connection, user_id: int) -> models.User:
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
        raise UserNotFoundException

    user = models.User(**user_data)
    return user


def db_get_user_list(connection, segment_length: int, index: int) -> List[models.User]:
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


def db_get_users_with_ids(connection, user_ids) -> List[models.User]:
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

    return users


def db_insert_user(connection, user: models.UserPost) -> models.User:
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

    except IntegrityError:
        raise UserNotUniqueException('Suggested user is not unique.')


def db_delete_user(connection, user_id: int) -> bool:

    where_stmnt = 'id = %s'

    user = db_get_user_safe_with_id(connection, user_id)

    if user is None:
        raise UserNotFoundException

    scopes = parse_scopes(user.scopes)

    if 'admin' in scopes:
        raise UnauthorizedOperationException("May not remove admin users this way")

    del_stmnt = MySQLStatementBuilder(connection)
    del_stmnt.delete(USERS_TABLE).where(where_stmnt, [user_id]).execute()

    return True

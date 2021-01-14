from .exceptions import UserNotFoundException, UserNotUniqueException
from .models import User
from apps.core.authentication.models import UserAuth
from apps.core.authentication.utils import get_password_hash, parse_scopes
from apps.core.authentication.exceptions import UnauthorizedOperationException
from libs.mysqlutils import MySQLStatementBuilder, FetchType
from mysql.connector.errors import IntegrityError


def get_user_safe_with_username(connection, user_name: str):
    mysql_statement = MySQLStatementBuilder(connection)
    cols = ['id', 'username', 'email', 'full_name']
    user_data = mysql_statement\
        .select('users', cols)\
        .where('username = %s', [user_name])\
        .execute(fetch_type=FetchType.FETCH_ONE, dictionary=True)

    if user_data is None:
        raise UserNotFoundException

    user = User(**user_data)
    return user


def get_user_safe_with_id(connection, user_id: int):
    try:
        int(user_id)
    except ValueError:
        raise TypeError

    cols_to_fetch = ['username', 'email', 'full_name', 'scopes']

    mysql_statement = MySQLStatementBuilder(connection)
    user_data = mysql_statement\
        .select('users', cols_to_fetch)\
        .where('id = %s', [user_id])\
        .execute(fetch_type=FetchType.FETCH_ONE, dictionary=True)

    if user_data is None:
        raise UserNotFoundException

    user = User(**user_data)
    return user


def get_user_list(connection, segment_length: int, index: int):
    try:
        int(segment_length)
        int(index)
        if index < 0:
            index = 0
        if segment_length < 1:
            segment_length = 1
    except ValueError:
        raise TypeError

    cols = ['id', 'username', 'email', 'full_name', 'scopes']
    mysql_statement = MySQLStatementBuilder(connection)
    users = mysql_statement\
        .select('users', cols)\
        .limit(segment_length)\
        .offset(segment_length * index)\
        .execute(fetch_type=FetchType.FETCH_ALL, dictionary=True)

    return users


def insert_user(connection, user: UserAuth):
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

        mysql_statement.insert('users', cols).set_values(vals).execute(fetch_type=FetchType.FETCH_NONE)
    except IntegrityError:
        raise UserNotUniqueException('Suggested user is not unique.')

    return User(**dict(user))


def delete_user(connection, user_id: int):

    where_stmnt = 'id = %s'

    user = get_user_safe_with_id(connection, user_id)

    if user is None:
        raise UserNotFoundException

    scopes = parse_scopes(user.scopes)

    if 'admin' in scopes:
        raise UnauthorizedOperationException("May not remove admin users this way")

    del_stmnt = MySQLStatementBuilder(connection)
    del_stmnt.delete('users').where(where_stmnt, [user_id]).execute()

    return True

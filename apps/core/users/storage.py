from .exceptions import UserNotFoundException, UserNotUniqueException
from .models import User
from apps.core.authentication.models import UserAuth
from apps.core.authentication.utils import get_password_hash
from libs.mysqlutils import MySQLStatementBuilder, FetchType
from mysql.connector.errors import IntegrityError


def get_user_safe_with_username(connection, user_name: str):
    cursor = connection.cursor(prepared=True)
    query = "SELECT id, username, email, full_name FROM users WHERE username = %s"
    cursor.execute(query, (user_name,))
    user_data = cursor.fetchone()

    if user_data is None:
        raise UserNotFoundException

    user_data = dict(zip(cursor.column_names, user_data))
    cursor.close()

    user = User(**user_data)
    return user


def get_user_safe_with_id(connection, user_id: int):
    try:
        int(user_id)
    except ValueError:
        raise TypeError

    cols_to_fetch = ['username', 'email', 'full_name']

    mysql_statement = MySQLStatementBuilder(connection)
    user_data = mysql_statement\
        .select('users', cols_to_fetch)\
        .where('id = %s', [user_id])\
        .execute(fetch_type=FetchType.FETCH_ONE)

    print(user_data)
    user_data = dict(zip(cols_to_fetch, user_data))
    print(user_data)
    user = User(**user_data)
    return user


def get_user_list(connection, segment_length: int, index: int):
    users = ['Pelle', 'Sture', 'Lotta', 'Eva']

    return users


def insert_user(connection, user: UserAuth):
    try:
        mysql_statement = MySQLStatementBuilder(connection)
        mysql_statement.insert('users',
                               ['username',
                                'password',
                                'email',
                                'full_name',
                                'scopes',
                                'disabled'],
                               [user.username,
                                get_password_hash(user.password),
                                user.email,
                                user.full_name,
                                user.scopes,
                                user.disabled]).execute(fetch_type=FetchType.FETCH_NONE)
    except IntegrityError:
        raise UserNotUniqueException('Suggested user is not unique.')

    return User(**dict(user))

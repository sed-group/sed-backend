from .exceptions import UserNotFoundException, UserNotUniqueException
from .models import User
from apps.core.authentication.models import UserAuth
from apps.core.authentication.utils import get_password_hash
from libs.mysqlutils import MySQLStatementBuilder
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

    cursor = connection.cursor(prepared=True)
    query = "SELECT id, username, email, full_name FROM users WHERE id = %s"
    cursor.execute(query, (user_id,))
    user_data = cursor.fetchone()

    if user_data is None:
        raise UserNotFoundException

    user_data = dict(zip(cursor.column_names, user_data))
    cursor.close()

    user = User(**user_data)
    return user


def get_user_list(connection, segment_length: int, index: int):
    users = ['Pelle', 'Sture', 'Lotta', 'Eva']

    return users


def insert_user(connection, user: UserAuth):
    try:
        mysql_statement = MySQLStatementBuilder(connection)
        mysql_statement.insert('users',
                               ('username',
                                'password',
                                'email',
                                'full_name',
                                'scopes',
                                'disabled'),
                               (user.username,
                                get_password_hash(user.password),
                                user.email,
                                user.full_name,
                                user.scopes,
                                user.disabled)).execute()
    except IntegrityError:
        raise UserNotUniqueException('Suggested user is not unique.')

    return User(**dict(user))

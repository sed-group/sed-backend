from .exceptions import UserNotFoundException
from .models import User


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


def get_user_list(connection, list_size: int, index: int):
    users = []

    return users


def create_user(connection, user: User):
    pass

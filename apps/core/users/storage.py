from .exceptions import UserNotFoundException
from .models import User


def get_user_safe_with_username(connection, user_name: str):
    cursor = connection.cursor(prepared=True)
    query = "SELECT id, username, email, full_name FROM users WHERE username = %s"
    cursor.execute(query, (user_name,))
    user_data = cursor.fetchone()
    user_data = dict(zip(cursor.column_names, user_data))
    cursor.close()

    if user_data is None:
        raise UserNotFoundException

    user = User(**user_data)
    return user


def get_user_safe_with_id(connection, user_id: int):
    cursor = connection.cursor(prepared=True)
    query = "SELECT id, username, email, full_name FROM users WHERE id = %s"
    cursor.execute(query, (user_id,))
    user_data = cursor.fetchone()
    user_data = dict(zip(cursor.column_names, user_data))
    cursor.close()

    if user_data is None:
        raise UserNotFoundException

    user = User(**user_data)
    return user

from .exceptions import UserNotFoundException
from .models import User


def get_user_safe(connection, user_id: int):
    cursor = connection.cursor(prepared=True)
    query = "SELECT id, username, email, full_name FROM users WHERE id = %s"
    cursor.execute(query, (user_id,))
    user_data = cursor.fetchone()

    if user_data is None:
        raise UserNotFoundException

    user = User(**user_data)
    return user

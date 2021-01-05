from .models import UserAuth
from apps.core.users.storage import get_user_safe


def get_user_auth_only(connection, user_id: int):
    """
    Get a fully populated user model. This is unsafe to use anywhere but during authorization.
    :param user_id: ID
    :return: UserAuth
    """
    user = get_user_safe(connection, user_id)
    user_auth = UserAuth(**user)

    cursor = connection.cursor(prepared=True)
    query = "SELECT password FROM users WHERE users.id = %s"
    cursor.execute(query, (user_id,))
    row = cursor.fetchone()
    user_auth.hashed_password = row.password

    return user_auth


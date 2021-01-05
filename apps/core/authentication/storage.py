from apps.core.authentication.models import UserAuth
from apps.core.users.exceptions import UserNotFoundException


def get_user_auth_only(connection, user_name: str):
    """
    Get a fully populated user model. This is unsafe to use anywhere but during authorization.
    :param connection: MySQL connection
    :param user_name: username
    :return: UserAuth
    """
    cursor = connection.cursor(prepared=True)
    query = "SELECT * FROM users WHERE username = %s"
    cursor.execute(query, (user_name,))
    user_data = cursor.fetchone()
    user_data = dict(zip(cursor.column_names, user_data))
    cursor.close()

    if user_data is None:
        raise UserNotFoundException

    user = UserAuth(**user_data)
    return user

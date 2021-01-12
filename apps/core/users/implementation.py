from fastapi import HTTPException, status

from apps.core.authentication.exceptions import UnauthorizedOperationException
from apps.core.users.exceptions import UserNotFoundException, UserNotUniqueException
from apps.core.authentication.models import UserAuth
from apps.core.users.models import User
from apps.core.db import get_connection
from apps.core.users.storage import get_user_safe_with_id, get_user_list, insert_user, delete_user


def impl_get_users_me(current_user: User):
    try:
        with get_connection() as con:
            user_safe = get_user_safe_with_id(con, current_user.id)
            return user_safe
    except UserNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User could not be found."
        )


def impl_get_users(segment_length: int, index: int):
    with get_connection() as con:
        user_list = get_user_list(con, segment_length, index)
        return user_list


def impl_get_user_with_id(user_id: int):
    try:
        with get_connection() as con:
            user_safe = get_user_safe_with_id(con, user_id)
            return user_safe
    except UserNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User with ID {} does not exist.".format(user_id)
        )
    except TypeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="user_id needs to be an integer"
        )


def impl_post_user(user: UserAuth):
    try:
        with get_connection() as con:
            insert_user(con, user)
            con.commit()
            return "Successfully created user"
    except UserNotUniqueException:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username is not unique",
        )


def impl_delete_user_from_db(user_id: int):
    try:
        with get_connection() as con:
            delete_user(con, user_id)
            con.commit()
            return "Successfully deleted user"
    except UnauthorizedOperationException:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You are not authorized to remove administrators"
        )
    except UserNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} could not be found"
        )

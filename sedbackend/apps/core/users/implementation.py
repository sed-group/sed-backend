from typing import List

from fastapi import HTTPException, status, File
from fastapi.logger import logger

from sedbackend.apps.core.authentication.exceptions import UnauthorizedOperationException
import sedbackend.apps.core.authentication.login as auth_login
import sedbackend.apps.core.authentication.exceptions as exc_auth
import sedbackend.apps.core.users.exceptions as exc
import sedbackend.apps.core.users.models as models
from sedbackend.apps.core.db import get_connection
import sedbackend.apps.core.users.storage as storage

import pandas as pd


def impl_get_users_me(current_user: models.User) -> models.User:
    try:
        with get_connection() as con:
            user_safe = storage.db_get_user_safe_with_id(con, current_user.id)
            return user_safe
    except exc.UserNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User could not be found."
        )


def impl_get_users(segment_length: int, index: int) -> List[models.User]:
    with get_connection() as con:
        user_list = storage.db_get_user_list(con, segment_length, index)
        return user_list


def impl_get_users_with_id(user_ids: List[int]) -> List[models.User]:
    with get_connection() as con:
        user_list = storage.db_get_users_with_ids(con, user_ids)
        return user_list


def impl_get_user_with_id(user_id: int) -> models.User:
    try:
        with get_connection() as con:
            user_safe = storage.db_get_user_safe_with_id(con, user_id)
            return user_safe
    except exc.UserNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User with ID {} does not exist.".format(user_id)
        )
    except TypeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="user_id needs to be an integer"
        )


def impl_get_user_with_username(username: str) -> models.User:
    try:
        with get_connection() as con:
            user_safe = storage.db_get_user_safe_with_username(con, username)
            return user_safe
    except exc.UserNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'User with username "{username}" does not exist.'
        )


def impl_post_user(user: models.UserPost) -> models.User:
    try:
        with get_connection() as con:
            res = storage.db_insert_user(con, user)
            con.commit()
            return res
    except exc.UserNotUniqueException:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username is not unique",
        )


def impl_post_users_bulk(file: File):
    logger.info("Bulk user creation requested.")
    try:
        with get_connection() as con:
            df = pd.read_excel(file)
            cols = list(df.columns)

            if "username" not in cols or "password" not in cols:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="Sheet needs to include columns \"username\" and \"password\" in lower-case."
                )

            for index, row in df.iterrows():
                user = models.UserPost(username=row["username"], password=row["password"], scopes="user")
                storage.db_insert_user(con, user)

            logger.info(f'Added {index} new users through bulk insertion.')

            con.commit()

    except exc.UserNotUniqueException:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Encountered non-unique username in bulk insertion."
        )


def impl_delete_user_from_db(user_id: int) -> bool:
    try:
        with get_connection() as con:
            res = storage.db_delete_user(con, user_id)
            con.commit()
            return res
    except UnauthorizedOperationException:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You are not authorized to remove administrators"
        )
    except exc.UserNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} could not be found"
        )


def impl_update_user_password(current_user: models.User, user_id: int, current_password: str, new_password: str) -> bool:
    try:
        if check_if_current_user_or_admin(current_user, user_id) is False:
            auth_login.authenticate_user(current_user.username, current_password)

        with get_connection() as connection:
            storage.db_update_user_password(connection, user_id, new_password)
            connection.commit()
            return True
    except exc.UserNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"No user with ID = {user_id} was found."
        )
    except exc_auth.InvalidCredentialsException:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Current password incorrect."
        )


def impl_update_user_details(current_user: models.User,
                             user_id:int,
                             update_details_request: models.UpdateDetailsRequest) -> bool:
    try:
        if check_if_current_user_or_admin(current_user, user_id) is False:
            return False

        with get_connection() as connection:
            storage.db_update_user_details(connection, user_id, update_details_request)
            connection.commit()

    except exc.UserNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"No user with ID = {user_id} was found."
        )

    return True


def check_if_current_user_or_admin(current_user, user_id):
    if current_user.id == user_id:
        return True

    # Current user is not the targeted user
    # Check if Admin
    scopes = auth_login.parse_scopes_array(current_user.scopes)
    if 'admin' not in scopes:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not allowed to change the password of another user."
        )

    # Check if trying to change other admin
    target_user = impl_get_user_with_id(user_id)
    if 'admin' in auth_login.parse_scopes_array(target_user.scopes):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not allowed to change administrator details."
        )

    return True

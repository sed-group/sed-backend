from fastapi import APIRouter, Depends, Response, status, Security, HTTPException

from apps.core.authentication.exceptions import UnauthorizedOperationException
from apps.core.authentication.utils import verify_token, get_current_active_user
from apps.core.authentication.models import UserAuth
from apps.core.users.models import User
from apps.core.db import get_connection
from apps.core.users.storage import get_user_safe_with_id, get_user_list, insert_user, delete_user
from apps.core.users.exceptions import UserNotFoundException, UserNotUniqueException

router = APIRouter()


@router.get("/me",
            summary="Returns logged in user")
async def get_users_me(current_user: User = Depends(get_current_active_user)):
    try:
        with get_connection() as con:
            user_safe = get_user_safe_with_id(con, current_user.id)
            return user_safe
    except UserNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User could not be found."
        )


@router.get("/list",
            summary="Lists all users",
            description="Produces a list of users in alphabetical order",
            dependencies=[Security(verify_token, scopes=['admin'])])
async def get_users(segment_length: int, index: int):
    with get_connection() as con:
        user_list = get_user_list(con, segment_length, index)
        return user_list


@router.get("/id/{user_id}",
            summary="Get user with ID",
            dependencies=[Security(verify_token, scopes=['admin'])])
async def get_user_with_id(user_id: int):
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


@router.post("/new",
             summary="Create new user",
             dependencies=[Security(verify_token, scopes=['admin'])])
async def post_user(user: UserAuth):
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


@router.delete("/id/{user_id}/delete",
               summary="Remove user from DB",
               dependencies=[Security(verify_token, scopes=['admin'])])
async def delete_user_from_db(user_id: int):
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


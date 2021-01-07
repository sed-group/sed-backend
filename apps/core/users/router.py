from fastapi import APIRouter, Depends, Response, status, Security

from apps.core.authentication.utils import verify_token, get_current_active_user
from apps.core.authentication.models import User
from apps.core.db import get_connection
from apps.core.users.storage import get_user_safe_with_id
from apps.core.users.exceptions import UserNotFoundException

router = APIRouter()


@router.get("/me",
            summary="Returns logged in user")
async def get_users_me(response: Response, current_user: User = Depends(get_current_active_user)):
    try:
        with get_connection() as con:
            user_safe = get_user_safe_with_id(con, current_user.id)
            return user_safe
    except UserNotFoundException:
        response.status_code = status.HTTP_404_NOT_FOUND
        return "User could not be found"


@router.get("/list",
            summary="Lists all users",
            description="Produces a list of users in alphabetical order",
            dependencies=[Security(verify_token, scopes=['admin'])])
async def get_users_list():
    return ["pelle", "sture", "bengt", "eva"]


@router.get("/id/{user_id}",
            summary="Get user with ID",
            dependencies=[Security(verify_token, scopes=['admin'])])
async def get_user_with_id(user_id, response: Response):
    try:
        with get_connection() as con:
            user_safe = get_user_safe_with_id(con, user_id)
            return user_safe
    except UserNotFoundException:
        response.status_code = status.HTTP_404_NOT_FOUND
        return "User with ID {} does not exist.".format(user_id)
    except TypeError:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return "user_id needs to be an integer"

from fastapi import APIRouter, Depends

from apps.core.authentication.utils import verify_token
from apps.core.authentication.models import User
from apps.core.db import get_connection
from apps.core.users.storage import get_user_safe_with_id

router = APIRouter()


@router.get("/me",
            summary="Returns logged in user",
            dependencies=[Depends(verify_token)])
async def get_users_me(current_user: User = Depends(verify_token)):
    con = get_connection()
    user_safe = get_user_safe_with_id(con, current_user.id)
    con.close()
    return user_safe


@router.get("/list",
            summary="Lists all users",
            description="Produces a list of users in alphabetical order",
            dependencies=[Depends(verify_token)])
async def get_users_list():
    return ["pelle", "sture", "bengt", "eva"]


@router.get("/id/{id}",
            summary="Get user with ID",
            dependencies=[Depends(verify_token)])
async def get_user_with_id(user_id):
    return {"user_id": "{}".format(user_id)}

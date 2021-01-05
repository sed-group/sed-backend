from fastapi import APIRouter, Depends

from apps.core.authentication.utils import verify_token
from apps.core.authentication.models import User

router = APIRouter()


@router.get("/me",
            summary="Returns logged in user")
async def get_users_me(current_user: User = Depends(verify_token)):
    return current_user


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

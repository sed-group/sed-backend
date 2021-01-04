from fastapi import APIRouter, Depends, HTTPException

from apps.core.authentication.utils import get_current_user, oauth2_scheme, fake_users_db, fake_hash_password
from apps.core.authentication.models import User, UserAuth

router = APIRouter()


@router.get("/me",
            tags=["users"],
            summary="Returns logged in user" )
async def get_users_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.get("/list",
            tags=["users"],
            summary="Lists all users",
            description="Produces a list of users in alphabetical order")
async def get_users_list(current_user: User = Depends(get_current_user)):
    return ["pelle", "sture", "bengt", "eva"]


@router.get("/id/{id}",
            tags=["users"],
            summary="Get user with ID")
async def get_user_with_id(user_id, current_user: User = Depends(get_current_user)):
    return {"user_id": "{}".format(user_id)}

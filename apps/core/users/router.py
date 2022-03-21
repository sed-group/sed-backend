from typing import List

from fastapi import APIRouter, Depends, Security

from apps.core.authentication.utils import get_current_active_user, verify_scopes
import apps.core.users.models as models
from apps.core.users.implementation import impl_get_users, impl_post_user, impl_delete_user_from_db, \
    impl_get_user_with_id, impl_get_users_me


router = APIRouter()


@router.get("",
            summary="Lists all users",
            description="Produces a list of users in alphabetical order",
            response_model=List[models.User])
async def get_users(segment_length: int, index: int):
    return impl_get_users(segment_length, index)


@router.post("",
             summary="Create new user",
             response_model=models.User,
             dependencies=[Security(verify_scopes, scopes=['admin'])])
async def post_user(user: models.UserPost):
    return impl_post_user(user)


@router.get("/me",
            summary="Returns logged in user",
            response_model=models.User)
async def get_users_me(current_user: models.User = Depends(get_current_active_user)):
    return impl_get_users_me(current_user)


@router.get("/{user_id}",
            summary="Get user with ID",
            response_model=models.User)
async def get_user_with_id(user_id: int):
    return impl_get_user_with_id(user_id)


@router.delete("/{user_id}",
               summary="Remove user from DB",
               response_model=bool,
               dependencies=[Security(verify_scopes, scopes=['admin'])])
async def delete_user_from_db(user_id: int):
    return impl_delete_user_from_db(user_id)

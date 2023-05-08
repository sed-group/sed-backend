from typing import List

from fastapi import APIRouter, Depends, Security, File, Request

from sedbackend.apps.core.authentication.utils import get_current_active_user, verify_scopes
import sedbackend.apps.core.users.models as models
from sedbackend.apps.core.users.implementation import impl_get_users, impl_post_user, impl_delete_user_from_db, \
    impl_get_user_with_id, impl_get_users_me, impl_post_users_bulk, impl_update_user_password


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


@router.post("/bulk",
             summary="Create array of new users from an xslx or csv sheet. "
                     "Needs to have two columns: \"username\" and \"password\".",
             # response_model=List[models.User],
             dependencies=[Security(verify_scopes, scopes=['admin'])])
async def post_users_bulk(file: bytes = File()):
    impl_post_users_bulk(file)
    return {"size": len(file)}


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


@router.put("/{user_id}/password",
            summary="Update user password",
            response_model=bool)
async def update_user_password(new_password_request: models.NewPasswordRequest,
                               current_user: models.User = Depends(get_current_active_user)):
    # User is either ADMIN or SAME AS EDITED USER
    return impl_update_user_password(current_user,
                                     new_password_request.user_id,
                                     new_password_request.current_password,
                                     new_password_request.new_password)


@router.put("/{user_id}/email",
            summary="Update user email",
            response_model=bool)
async def update_user_email(user_id: int, new_email: str,
                            current_user: models.User = Depends(get_current_active_user)):
    # User is either ADMIN or SAME AS EDITED USER
    pass


@router.put("/{user_id}/name",
            summary="Update user full name",
            response_model=bool)
async def update_user_email(user_id: int, full_name: str,
                            current_user: models.User = Depends(get_current_active_user)):
    # User is either ADMIN or SAME AS EDITED USER
    pass

from fastapi import APIRouter, Depends, Security
from fastapi.security import OAuth2PasswordRequestForm


import sedbackend.apps.core.authentication.implementation as impl
from sedbackend.apps.core.users.models import User
from sedbackend.apps.core.authentication.utils import get_current_active_user, verify_token


router = APIRouter()


@router.post("/token",
             summary="Login using token",
             description="Login using Token")
async def login_with_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Authenticates the user when logging in by comparing hashed password values
    """
    return impl.impl_login_with_token(form_data)


@router.get("/renew", dependencies=[Security(verify_token)])
async def renew_token(current_user: User = Depends(get_current_active_user)) -> str:
    """
    Renews an existing token. It takes an existing token, and returns a new one.
    :param current_user: User accessing this endpoint
    :return:
    """
    return impl.impl_renew_token(current_user)

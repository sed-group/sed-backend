from fastapi import APIRouter, Depends, Security, Request
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


@router.get("/sso_token", dependencies=[Security(verify_token)])
async def get_sso_token(request: Request, current_user: User = Depends(get_current_active_user)) -> str:
    """
    Get SSO token (nonce). Only lasts for a few seconds.
    :param request: client request object
    :param current_user: user object
    :return: Nonce string
    """
    return impl.impl_get_sso_token(current_user, request.client.host)


@router.post("/sso_token")
async def resolve_sso_token(request: Request, nonce: str):
    """
    Token for nonce trade. Turn in nonce within a limited time to retrieve an auth token
    :param request: client request object
    :param nonce: nonce token
    :return: Auth token string
    """
    return impl.impl_resolve_sso_token(nonce, request.client.host)

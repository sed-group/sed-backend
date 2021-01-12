from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from apps.core.authentication.implementation import impl_login_with_token

router = APIRouter()


@router.post("/token",
             summary="Login using token",
             description="Login using Token")
async def login_with_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Authenticates the user when logging in by comparing hashed password values
    """
    return impl_login_with_token(form_data)

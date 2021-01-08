from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.security import OAuth2PasswordRequestForm

from apps.core.authentication.login import authenticate_and_generate_access_token
from apps.core.authentication.exceptions import InvalidCredentialsException

router = APIRouter()


@router.post("/token",
             summary="Login using token",
             description="Login using Token")
async def login_with_token(response: Response, form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Authenticates the user when logging in by comparing hashed password values
    """

    try:
        access_token = authenticate_and_generate_access_token(form_data.username, form_data.password)
        response.set_cookie(key="access_token",
                            value=f'Bearer {access_token}',
                            httponly=True,
                            samesite='lax')
        return

    except InvalidCredentialsException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"}
        )

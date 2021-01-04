from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from apps.core.authentication.utils import login
from apps.core.authentication.exceptions import InvalidCredentialsException

router = APIRouter()


@router.post("/token")
async def login_with_token(form_data: OAuth2PasswordRequestForm = Depends()):
    '''
    Authenticates the user when logging in by comparing hashed password values
    '''

    try:
        return login(form_data.username, form_data.password)
    except InvalidCredentialsException:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"}
        )

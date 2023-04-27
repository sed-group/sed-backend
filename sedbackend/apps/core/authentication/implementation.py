from datetime import timedelta

from fastapi.security import OAuth2PasswordRequestForm
from fastapi import HTTPException, status

from sedbackend.apps.core.authentication.exceptions import InvalidCredentialsException
from sedbackend.apps.core.authentication.login import login, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from sedbackend.apps.core.authentication.utils import parse_jwt_token, parse_scopes
from sedbackend.apps.core.users.exceptions import UserDisabledException
from sedbackend.apps.core.users.models import User


def impl_login_with_token(form_data: OAuth2PasswordRequestForm):
    try:
        return login(form_data.username, form_data.password)
    except InvalidCredentialsException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"}
        )
    except UserDisabledException:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User has been suspended",
            headers={"WWW-Authenticate": "Bearer"}
        )


def impl_renew_token(user: User):
    try:

        return create_access_token(
            data={"sub": user.username, "scopes": parse_scopes(user.scopes)},
            expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        )
    except UserDisabledException:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User has been suspended"
        )

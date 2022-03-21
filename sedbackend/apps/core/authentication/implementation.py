from fastapi.security import OAuth2PasswordRequestForm
from fastapi import HTTPException, status

from sedbackend.apps.core.authentication.exceptions import InvalidCredentialsException
from sedbackend.apps.core.authentication.login import login
from sedbackend.apps.core.users.exceptions import UserDisabledException


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

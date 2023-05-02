from datetime import timedelta

from fastapi.security import OAuth2PasswordRequestForm
from fastapi import HTTPException, status

import sedbackend.apps.core.authentication.storage as storage
import sedbackend.apps.core.authentication.exceptions as exc
from sedbackend.apps.core.authentication.login import login, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from sedbackend.apps.core.authentication.utils import parse_scopes
from sedbackend.apps.core.users.exceptions import UserDisabledException
from sedbackend.apps.core.users.models import User
from sedbackend.apps.core.users.storage import db_get_user_safe_with_id
from sedbackend.apps.core.db import get_connection


def impl_login_with_token(form_data: OAuth2PasswordRequestForm):
    try:
        return login(form_data.username, form_data.password)
    except exc.InvalidCredentialsException:
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


def impl_get_sso_token(current_user: User, ip: str) -> str:
    try:
        with get_connection() as con:
            nonce = storage.db_insert_sso_token(con, current_user.id, ip)
            con.commit()
            if nonce is None:
                raise exc.FaultyNonceOperation

            return nonce
    except UserDisabledException:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User has been suspended"
        )
    except exc.FaultyNonceOperation:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="SSO operation failed."
        )


def impl_resolve_sso_token(nonce: str, ip: str) -> str:
    try:
        with get_connection() as con:
            user_id = storage.db_resolve_sso_token(con, ip, nonce)
            if user_id is None:
                raise exc.InvalidNonceException
            con.commit()

            user = db_get_user_safe_with_id(con, user_id)

            return impl_renew_token(user)
    except exc.InvalidNonceException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token not valid"
        )
    except exc.FaultyNonceOperation:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Resolution of token failed due to server error."
        )

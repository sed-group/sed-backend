from datetime import timedelta, datetime
from typing import Optional

from jose import jwt
from passlib.context import CryptContext

from apps.core.authentication.exceptions import InvalidCredentialsException
from apps.core.authentication.storage import get_user_auth_only
from apps.core.db import get_connection


# TODO: Change secret key. Use `openssl rand -hex 32`.
SECRET_KEY  = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM   = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def login(username, plain_pwd, scopes):
    user = authenticate_user(username, plain_pwd)
    if not user:
        raise InvalidCredentialsException()
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "scopes": scopes},
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


def authenticate_user(username: str, password: str):
    user = get_user_with_pwd_from_db(username)
    if not user:
        # User does not exist
        return False
    if not verify_password(password, user.password):
        # Password is incorrect
        return False

    # If the credentials are correct, then return the user
    return user


def get_password_hash(plain_pwd):
    return pwd_context.hash(plain_pwd)


def get_user_with_pwd_from_db(username: str):
    """
    Only for use when authenticating a user
    :param username: Username
    :return:
    """
    with get_connection() as con:
        user_auth = get_user_auth_only(con, username)
        return user_auth


def verify_password(plain_pwd, hashed_pwd):
    return pwd_context.verify(plain_pwd, hashed_pwd)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

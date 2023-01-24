from datetime import timedelta, datetime
from typing import Optional

from jose import jwt
from passlib.context import CryptContext

from sedbackend.apps.core.users.exceptions import UserNotFoundException, UserDisabledException
from sedbackend.apps.core.authentication.models import UserAuth
from sedbackend.apps.core.authentication.exceptions import InvalidCredentialsException
from sedbackend.apps.core.authentication.storage import get_user_auth_only
from sedbackend.apps.core.db import get_connection
from sedbackend.env import Environment


# Key can be created using `openssl rand -hex 32`.
SECRET_KEY  = Environment.get_variable('JWT_KEY')
ALGORITHM   = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30 
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def login(username, plain_pwd):
    user, scopes = authenticate_user(username, plain_pwd)
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
        raise InvalidCredentialsException
    if user.disabled:
        raise UserDisabledException
    if not verify_password(password, user.password):
        # Password is incorrect
        raise InvalidCredentialsException

    scopes = parse_user_scopes(user)

    # If the credentials are correct, then return the user
    return user, scopes


def get_user_with_pwd_from_db(username: str) -> UserAuth:
    """
    Only for use when authenticating a user
    :param username: Username
    :return:
    """
    try:
        with get_connection() as con:
            user_auth = get_user_auth_only(con, username)
            return user_auth
    except UserNotFoundException:
        raise InvalidCredentialsException


def verify_password(plain_pwd, hashed_pwd):
    return pwd_context.verify(plain_pwd, hashed_pwd)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=60)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def parse_user_scopes(user):
    scopes = []
    if user.scopes:
        scopes = parse_scopes_array(user.scopes)
    return scopes


def parse_scopes_array(scopes_array):
    scopes = scopes_array.split(';')
    return scopes

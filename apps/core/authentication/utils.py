from typing import Optional
from fastapi import Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import JWTError, jwt

from apps.core.db import get_connection
from apps.core.users.models import User
from apps.core.authentication.models import TokenData
from apps.core.authentication.exceptions import InvalidCredentialsException
from apps.core.authentication.storage import get_user_auth_only

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/core/auth/token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# TODO: Change secret key. Use `openssl rand -hex 32`.
SECRET_KEY  = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM   = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def get_user(username: str):
    con = get_connection()
    user_auth = get_user_auth_only(con, username)
    con.close()
    return user_auth


async def verify_token(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception

    user = get_user(username=token_data.username)
    # Requested user does not exist
    if not user:
        raise credentials_exception
    return user


async def get_current_active_user(current_user: User = Depends(verify_token)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")


def verify_password(plain_pwd, hashed_pwd):
    return pwd_context.verify(plain_pwd, hashed_pwd)


def get_password_hash(plain_pwd):
    return pwd_context.hash(plain_pwd)


def authenticate_user(username: str, password: str):
    user = get_user(username)
    if not user:
        # User does not exist
        return False
    if not verify_password(password, user.password):
        # Password is incorrect
        return False

    # If the credentials are correct, then return the user
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def login(username, plain_pwd):
    user = authenticate_user(username, plain_pwd)
    if not user:
        raise InvalidCredentialsException()
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

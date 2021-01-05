from fastapi import Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

from apps.core.authentication.login import get_user_with_pwd_from_db, SECRET_KEY, ALGORITHM
from apps.core.authentication.models import TokenData

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/core/auth/token")


async def verify_token(token: str = Depends(oauth2_scheme)):
    """
    Can be used as a dependency to check if a user is logged in.
    This is done by asserting that the session token exists and has not expired.
    :param token: The token
    :return: The user
    """
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

    user = get_user_with_pwd_from_db(username=token_data.username)
    # Requested user does not exist
    if not user:
        raise credentials_exception
    return user

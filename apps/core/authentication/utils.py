from fastapi import Depends, status, HTTPException, Security
from fastapi.security import OAuth2PasswordBearer, SecurityScopes
from jose import JWTError, jwt
from pydantic import ValidationError

from apps.core.authentication.login import get_user_with_pwd_from_db, SECRET_KEY, ALGORITHM
from apps.core.authentication.models import TokenData
from apps.core.users.models import User

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/core/auth/token",
    scopes={
        "me": "Read information about current user",
        "items": "Read items"
    }
)


async def verify_token(security_scopes: SecurityScopes, token: str = Depends(oauth2_scheme)):
    """
    Can be used as a dependency to check if a user is logged in.
    This is done by asserting that the session token exists and has not expired.
    :param security_scopes: Clearance/permissions
    :param token: The token
    :return: The user
    """
    if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
    else:
        authenticate_value = f"Bearer"

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": authenticate_value}
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_scopes = payload.get("scopes", [])
        token_data = TokenData(scopes=token_scopes, username=username)
    except (JWTError, ValidationError):
        raise credentials_exception

    user = get_user_with_pwd_from_db(username=token_data.username)
    # Requested user does not exist
    if not user:
        raise credentials_exception

    for scope in security_scopes.scopes:
        print("Is {} in {}?".format(scope, str(token_data.scopes)))
        if scope not in token_data.scopes:
            print("No.")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Permission denied",
                headers={"WWW-Authenticate": authenticate_value}
            )
        else:
            print('Yes.')
    print("Return user")
    return user


async def get_current_active_user(current_user: User = Security(verify_token, scopes=["me"])):
    print("GET CURRENT ACTIVE USER")
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

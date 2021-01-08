from typing import Optional, List
from pydantic import BaseModel
from fastapi.security.oauth2 import OAuthFlowsModel, get_authorization_scheme_param
from fastapi.security import OAuth2
from fastapi import Request, HTTPException, status

from apps.core.users.models import User


class UserAuth(User):
    """
    SHOULD ONLY BE USED DURING AUTHENTICATION PROCESSES.
    User model that also contains the hashed password.
    """
    password: str
    scopes: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None
    scopes: List[str] = []


class OAuth2PasswordBearerWithCookie (OAuth2):
    def __init__(
            self,
            tokenUrl: str,
            scheme_name: str = None,
            scopes: dict = None,
            auto_error: bool = True):
        if not scopes:
            scopes = {}
        flows = OAuthFlowsModel(password={"tokenUrl": tokenUrl, "scopes": scopes})
        super().__init__(flows=flows, scheme_name=scheme_name, auto_error=auto_error)

    async def __call__(self, request: Request) -> Optional[str]:
        authorization: str = request.cookies.get("access_token")

        scheme, param = get_authorization_scheme_param(authorization)
        if not authorization or scheme.lower() != "bearer":
            if self.auto_error:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Not authenticated",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            else:
                return None

        return param




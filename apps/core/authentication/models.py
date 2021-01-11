from typing import Optional, List
from pydantic import BaseModel

from apps.core.users.models import User


class UserAuth(User):
    """
    SHOULD ONLY BE USED DURING AUTHENTICATION PROCESSES, OR WHEN CREATING A NEW USER.
    """
    password: str
    scopes: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None
    scopes: List[str] = []

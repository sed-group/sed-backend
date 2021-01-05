from typing import Optional
from pydantic import BaseModel

from apps.core.users.models import User


class UserAuth(User):
    """
    SHOULD ONLY BE USED DURING AUTHENTICATION PROCESSES.
    User model that also contains the hashed password.
    """
    hashed_password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None

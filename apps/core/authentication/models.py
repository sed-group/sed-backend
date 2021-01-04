from typing import Optional

from pydantic import BaseModel


class User(BaseModel):
    """
    Standard user model containing only "safe" information.
    """
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = None


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

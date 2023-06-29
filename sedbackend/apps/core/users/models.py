from pydantic import BaseModel
from typing import Optional


class User(BaseModel):
    """
    Standard user model containing only "safe" information.
    """
    id: Optional[int] = None
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = None
    scopes: str = None


class UserPost(BaseModel):
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = False
    password: str
    scopes: str = None


class NewPasswordRequest(BaseModel):
    current_password: Optional[str]
    new_password: str


class UpdateDetailsRequest(BaseModel):
    email: str
    full_name: str

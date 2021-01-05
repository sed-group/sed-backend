from pydantic import BaseModel
from typing import Optional


class User(BaseModel):
    """
    Standard user model containing only "safe" information.
    """
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = None


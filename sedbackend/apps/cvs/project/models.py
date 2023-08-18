from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from sedbackend.apps.core.users.models import User


class CVSProject(BaseModel):
    id: int
    name: str = Field(..., max_length=255)
    description: Optional[str] = None
    currency: Optional[str] = Field(None, max_length=10)
    owner: User
    datetime_created: datetime
    my_access_right: int


class CVSProjectPost(BaseModel):
    name: str = Field(..., max_length=255)
    description: Optional[str] = None
    currency: Optional[str] = Field(None, max_length=10)

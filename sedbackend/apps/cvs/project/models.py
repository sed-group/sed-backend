from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from sedbackend.apps.core.users.models import User


class CVSProject(BaseModel):
    id: int
    name: str
    description: str
    currency: str
    owner: User
    datetime_created: datetime


class CVSProjectPost(BaseModel):
    name: str
    description: Optional[str] = None
    currency: Optional[str] = None

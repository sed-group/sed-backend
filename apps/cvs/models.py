from typing import Optional

from datetime import datetime
from pydantic import BaseModel

from apps.core.users.models import User


class CVSProject(BaseModel):
    id: int
    name: str
    description: str
    owner: User
    datetime_created: datetime


class CVSProjectPost(BaseModel):
    name: str
    description: Optional[str] = None

from datetime import datetime
from typing import Optional, List, Dict
from pydantic import BaseModel, Field
from sedbackend.apps.core.projects.models import AccessLevel
from sedbackend.apps.core.users.models import User
import sedbackend.apps.core.projects.models as proj_models


class CVSProject(BaseModel):
    id: int
    name: str = Field(..., max_length=255)
    description: Optional[str] = None
    currency: Optional[str] = Field(None, max_length=10)
    owner: User
    datetime_created: datetime
    my_access_right: int
    project: proj_models.Project = None
    subproject: proj_models.SubProject = None



class CVSProjectPost(BaseModel):
    name: str = Field(..., max_length=255)
    description: Optional[str] = None
    currency: Optional[str] = Field(None, max_length=10)
    participants: Optional[List[int]] = []
    participants_access: Optional[Dict[int, AccessLevel]] = {}

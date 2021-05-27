from pydantic import BaseModel

from typing import Optional, List, Dict
from enum import IntEnum, unique

from apps.core.users.models import User


@unique
class AccessLevel(IntEnum):
    NONE = 0
    READONLY = 1
    EDITOR = 2
    ADMIN = 3
    OWNER = 4


class Project(BaseModel):
    id: Optional[int] = None        # Project database ID
    name: Optional[str] = None      # Name of the project
    subprojects: List[int] = []     # Mappings to application subproject IDs
    participants: List[User] = []   # List of users who has any kind of access to this project
    participants_access: Dict[int, AccessLevel] = dict()   # Maps user_id to access_type


class ProjectListing(BaseModel):
    id: int
    name: str
    access_level: AccessLevel = AccessLevel.NONE


class ProjectPost(BaseModel):
    name: str
    participants: List[int]
    participants_access: Dict[int, AccessLevel]


class SubProject(BaseModel):
    id: int
    application_sid: str
    project_id: int
    native_project_id: int

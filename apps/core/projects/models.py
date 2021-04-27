from pydantic import BaseModel

from typing import Optional, List, Dict
from enum import Enum, unique

from apps.core.users.models import User


@unique
class AccessLevel(Enum):
    NONE = 0
    READONLY = 1
    EDITOR = 2
    ADMIN = 3
    OWNER = 4


@unique
class AccessType(Enum):
    READ = 0
    WRITE = 1
    ADMIN = 2
    ANY = 3


class Project(BaseModel):
    id: Optional[int] = None        # Project database ID
    name: Optional[str] = None      # Name of the project
    subprojects: List[int] = []     # Mappings to application subproject IDs
    participants: List[User] = []   # List of users who has any kind of access to this project
    participants_access: Dict[int, int] = dict()   # Maps user_id to access_type

    def has_access(self, user_id: int) -> AccessLevel:
        # Check in database if user has access to this project, and what kind of access.
        pass


class ProjectListing(BaseModel):
    id: int
    name: str


class ProjectPost(BaseModel):
    name: str
    participants: List[int]
    participants_access: Dict[int, int]



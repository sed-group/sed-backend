from pydantic import BaseModel
from typing import Optional, List
from enum import Enum, unique

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

    def has_access(self, user_id: int) -> AccessLevel:
        # Check in database if user has access to this project, and what kind of access.
        pass


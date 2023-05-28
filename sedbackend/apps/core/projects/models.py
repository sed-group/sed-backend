from __future__ import annotations          # Obsolete in Python 3.10
from typing import Optional, List, Dict
from enum import IntEnum, unique
from datetime import datetime

from pydantic import BaseModel, constr

from sedbackend.apps.core.users.models import User


@unique
class AccessLevel(IntEnum):
    NONE = 0
    READONLY = 1
    EDITOR = 2
    ADMIN = 3
    OWNER = 4

    @staticmethod
    def list_can_read() -> List[AccessLevel]:
        return [AccessLevel.READONLY, AccessLevel.EDITOR, AccessLevel.ADMIN, AccessLevel.OWNER]

    @staticmethod
    def list_can_edit() -> List[AccessLevel]:
        return [AccessLevel.EDITOR, AccessLevel.ADMIN, AccessLevel.OWNER]

    @staticmethod
    def list_are_admins() -> List[AccessLevel]:
        return [AccessLevel.ADMIN, AccessLevel.OWNER]


class ProjectListing(BaseModel):
    id: int
    name: str
    access_level: AccessLevel = AccessLevel.NONE


class ProjectPost(BaseModel):
    name: constr(min_length=5)
    participants: List[int]
    participants_access: Dict[int, AccessLevel]


class SubProjectPost(BaseModel):
    name: Optional[constr(min_length=5)] = 'Unnamed sub-project'
    application_sid: str
    native_project_id: int


class SubProject(SubProjectPost):
    id: int
    name: str = None
    owner_id: int
    project_id: Optional[int]
    native_project_id: int
    datetime_created: datetime


class Project(BaseModel):
    id: Optional[int] = None        # Project database ID
    name: Optional[str] = None      # Name of the project
    subprojects: List[SubProject] = []     # Mappings to application subproject IDs
    participants: List[User] = []   # List of users who has any kind of access to this project
    participants_access: Dict[int, AccessLevel] = dict()   # Maps user_id to access_type

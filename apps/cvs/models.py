from typing import Optional

from datetime import datetime
from pydantic import BaseModel

from apps.core.users.models import User


# ======================================================================================================================
# CVS projects
# ======================================================================================================================

class CVSProject(BaseModel):
    id: int
    name: str
    description: str
    owner: User
    datetime_created: datetime


class CVSProjectPost(BaseModel):
    name: str
    description: Optional[str] = None


# ======================================================================================================================
# VCS (Value Creation Strategy)
# ======================================================================================================================

class VCS(BaseModel):
    id: int
    name: str
    description: str
    project: CVSProject
    datetime_created: datetime
    year_from: int
    year_to: int


class VCSPost(BaseModel):
    name: str
    description: Optional[str] = None
    year_from: Optional[int] = None
    year_to: Optional[int] = None


# ======================================================================================================================
# VCS ISO Process
# ======================================================================================================================

class VCSISOProcess(BaseModel):
    id: int
    name: str
    group: str


# ======================================================================================================================
# VCS Subprocess
# ======================================================================================================================

class VCSSubprocess(BaseModel):
    id: int
    name: str
    parent_process: VCSISOProcess


class VCSSubprocessPost(BaseModel):
    name: str
    parent_process_id: int


# ======================================================================================================================
# VCS Stakeholder need
# ======================================================================================================================

class VCSTableRow(BaseModel):
    id: int
    stakeholder: str
    stakeholder_expectations: str
    iso_process: VCSISOProcess
    subprocess: VCSSubprocess
    vcs: VCS


class VCSTableRowPost(BaseModel):
    stakeholder: str
    stakeholder_expectations: Optional[str] = None
    iso_process_id: Optional[int] = None
    subprocess_id: Optional[int] = None


# ======================================================================================================================
# VCS Stakeholder need
# ======================================================================================================================

class VCSStakeholderNeed(BaseModel):
    id: int
    name: str
    rank_weight: int
    vcs_tabel_row: VCSTableRow


class VCSStakeholderNeedPost(BaseModel):
    name: str
    rank_weight: int


# ======================================================================================================================
# VCS Value driver
# ======================================================================================================================

class VCSValueDriver(BaseModel):
    id: int
    name: str
    project: CVSProject


class VCSValueDriverPost(BaseModel):
    name: str

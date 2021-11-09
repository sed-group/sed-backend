from typing import Optional
import enum

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


class VCSISOProcess:
    def __init__(self, id: int, name: str, category: str):
        self.id = id
        self.name = name
        self.category = category


class VCSISOProcesses(enum.Enum):  # processes in ISO 15288
    # Agreement Processes
    _01 = VCSISOProcess(id=1, name='Acquisition', category='Agreement Processes')
    _02 = VCSISOProcess(id=2, name='Supply', category='Agreement Processes')

    # Organizational project-enabling processes
    _03 = VCSISOProcess(id=3, name='Life-cycle model management', category='Organizational project-enabling processes')
    _04 = VCSISOProcess(id=4, name='Infrastructure management', category='Organizational project-enabling processes')
    _05 = VCSISOProcess(id=5, name='Project portfolio management', category='Organizational project-enabling processes')
    _06 = VCSISOProcess(id=6, name='Human resource management', category='Organizational project-enabling processes')
    _07 = VCSISOProcess(id=7, name='Quality management', category='Organizational project-enabling processes')

    # Project processes
    _08 = VCSISOProcess(id=8, name='Project planning', category='Project processes')
    _09 = VCSISOProcess(id=9, name='Project assessment and control', category='Project processes')
    _10 = VCSISOProcess(id=10, name='Decision management', category='Project processes')
    _11 = VCSISOProcess(id=11, name='Risk management', category='Project processes')
    _12 = VCSISOProcess(id=12, name='Configuration management', category='Project processes')
    _13 = VCSISOProcess(id=13, name='Information management', category='Project processes')
    _14 = VCSISOProcess(id=14, name='Measurement', category='Project processes')

    # Technical processes
    _15 = VCSISOProcess(id=15, name='Stakeholder requirements definition', category='Technical processes')
    _16 = VCSISOProcess(id=16, name='Requirements analysis', category='Technical processes')
    _17 = VCSISOProcess(id=17, name='Architectual design', category='Technical processes')
    _18 = VCSISOProcess(id=18, name='Implementation', category='Technical processes')
    _19 = VCSISOProcess(id=19, name='Integration', category='Technical processes')
    _20 = VCSISOProcess(id=20, name='Verification', category='Technical processes')
    _21 = VCSISOProcess(id=21, name='Transition', category='Technical processes')
    _22 = VCSISOProcess(id=22, name='Validation', category='Technical processes')
    _23 = VCSISOProcess(id=23, name='Operation', category='Technical processes')
    _24 = VCSISOProcess(id=24, name='Maintenance', category='Technical processes')
    _25 = VCSISOProcess(id=25, name='Disposal', category='Technical processes')


# ======================================================================================================================
# VCS Subprocess
# ======================================================================================================================

class VCSSubprocess(BaseModel):
    id: int
    name: str
    parent_process: VCSISOProcess
    project: CVSProject


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

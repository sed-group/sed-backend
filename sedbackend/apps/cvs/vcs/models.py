from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, confloat
from sedbackend.apps.cvs.project.models import CVSProject


# ======================================================================================================================
# VCS (Value Creation Strategy)
# ======================================================================================================================


class VCS(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    project: CVSProject
    datetime_created: datetime
    year_from: int
    year_to: int


class VCSPost(BaseModel):
    name: str
    description: Optional[str] = None
    year_from: int
    year_to: int


# ======================================================================================================================
# VCS ISO Process
# ======================================================================================================================


class VCSISOProcess(BaseModel):
    id: int
    name: str
    category: str


# ======================================================================================================================
# VCS Subprocess
# ======================================================================================================================

class VCSSubprocess(BaseModel):
    id: int
    project_id: int
    name: str
    parent_process: VCSISOProcess


class VCSSubprocessPost(BaseModel):
    name: str
    parent_process_id: int


class VCSSubprocessPut(BaseModel):
    name: str
    parent_process_id: int


# ======================================================================================================================
# VCS Value dimension
# ======================================================================================================================


class ValueDimension(BaseModel):
    id: int
    name: str
    priority: str
    vcs_row: int


class ValueDimensionPost(BaseModel):
    name: str
    priority: str


# ======================================================================================================================
# VCS Value driver
# ======================================================================================================================


class ValueDriver(BaseModel):
    id: int
    name: str
    unit: Optional[str] = None
    projects: Optional[List[int]] = None

class ValueDriverPost(BaseModel):
    name: str
    unit: Optional[str] = None
    project_id: int


# ======================================================================================================================
# VCS Stakeholder Need
# ======================================================================================================================


class StakeholderNeed(BaseModel):
    id: int
    need: str
    rank_weight: Optional[confloat(ge=0, le=1)] = None
    value_dimension: Optional[str] = None
    value_drivers: Optional[List[ValueDriver]] = None


class StakeholderNeedPost(BaseModel):
    id: Optional[int] = None
    need: str
    value_dimension: Optional[str] = None
    value_drivers: Optional[List[int]] = None
    rank_weight: Optional[confloat(ge=0, le=1)] = None


# ======================================================================================================================
# VCS Rows - Representation/return models
# ======================================================================================================================

class VcsRow(BaseModel):
    id: int
    vcs_id: int
    index: int
    stakeholder: str
    stakeholder_needs: Optional[List[StakeholderNeed]] = None
    stakeholder_expectations: str
    iso_process: Optional[VCSISOProcess] = None
    subprocess: Optional[VCSSubprocess] = None


class VcsRowPost(BaseModel):
    id: Optional[int] = None
    index: int
    stakeholder: str
    stakeholder_needs: Optional[List[StakeholderNeedPost]] = None
    stakeholder_expectations: str
    iso_process: Optional[int] = None
    subprocess: Optional[int] = None

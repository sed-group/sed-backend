import enum
from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel

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
    vcs_id: int
    name: str
    order_index: int
    parent_process: VCSISOProcess


class VCSSubprocessPost(BaseModel):
    name: str
    order_index: int
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


class ValueDriverPost(BaseModel):
    name: str


# ======================================================================================================================
# VCS Stakeholder Need
# ======================================================================================================================


class StakeholderNeed(BaseModel):
    id: int
    #vcs_row_id: int
    need: str
    rank_weight: Optional[float] = None
    value_dimension: Optional[str] = None
    value_drivers: Optional[List[ValueDriver]] = None


"""
Not used anywhere - Remove?
class StakeholderNeedPut(BaseModel):
    id: int
    vcs_row_id: int
    need: str
    value_dimension: Optional[str] = None
    value_drivers: Optional[List[int]] = None
    rank_weight: Optional[float] = None
"""

class StakeholderNeedPost(BaseModel):
    id: Optional[int] = None
    #vcs_row_id: Optional[int] = None
    need: str
    value_dimension: Optional[str] = None
    value_drivers: Optional[List[int]] = None
    rank_weight: Optional[float] = None


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

"""
Not used anywhere - Remove?
class VcsRowPut(BaseModel):
    id: int
    vcs_id: int
    index: int
    stakeholder: str
    stakeholder_needs: Optional[List[StakeholderNeedPut]] = None
    stakeholder_expectations: str
    iso_process: Optional[int] = None
    subprocess: Optional[int] = None
"""

class VcsRowPost(BaseModel):
    id: Optional[int] = None
    vcs_id: Optional[int] = None
    index: int
    stakeholder: str
    stakeholder_needs: Optional[List[StakeholderNeedPost]] = None
    stakeholder_expectations: str
    iso_process: Optional[int] = None
    subprocess: Optional[int] = None



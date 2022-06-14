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
    unit: Optional[str] = None
    value_dimension: Optional[int] = None


class ValueDriverPost(BaseModel):
    name: str
    unit: Optional[str] = None
    value_dimension: Optional[int] = None

# ======================================================================================================================
# VCS Rows - Representation/return models
# ======================================================================================================================

class VcsRow(BaseModel):
    id: int
    index: int
    stakeholder: str
    stakeholder_needs: str
    stakeholder_expectations: str
    iso_process: Optional[VCSISOProcess] = None
    subprocess: Optional[VCSSubprocess] = None
    value_dimensions: Optional[List[ValueDimension]] = None
    value_drivers: Optional[List[ValueDriver]] = None
    vcs_id: int

class VcsRowPost(BaseModel):
    index: int
    stakeholder: str
    stakeholder_needs: str
    stakeholder_expectations: str
    iso_process: Optional[int] = None
    subprocess: Optional[int] = None
    value_dimensions: Optional[List[ValueDimensionPost]] = None
    value_drivers: Optional[List[int]] = None


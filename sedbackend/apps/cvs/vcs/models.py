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
    order_index: int
    project: CVSProject


class VCSSubprocessPost(BaseModel):
    name: str
    parent_process_id: int
    order_index: int


# ======================================================================================================================
# VCS Table Row
# ======================================================================================================================

class VCSTableRow(BaseModel):
    id: int
    node_id: int
    row_index: int
    stakeholder: str
    stakeholder_expectations: str
    iso_process: VCSISOProcess
    subprocess: VCSSubprocess
    vcs: VCS


class VCSTableRowPost(BaseModel):  # Never used anywhere
    node_id: Optional[int] = None
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
    name: Optional[str] = None
    rank_weight: Optional[int] = None


# ======================================================================================================================
# VCS Value driver
# ======================================================================================================================


class VCSValueDriver(BaseModel):
    id: int
    name: str
    unit: Optional[str] = None
    project: CVSProject


class VCSValueDriverPost(BaseModel):
    name: str
    unit: Optional[str] = None


class ValueDriverGet(BaseModel):
    id: int
    name: str
    unit: Optional[str] = None


# ======================================================================================================================
# VCS Table - Representation/return models
# ======================================================================================================================


class StakeholderNeedGet(BaseModel):
    id: int
    need: str
    rank_weight: int
    value_drivers: List[ValueDriverGet] = None


class TableRowGet(BaseModel):
    id: int
    node_id: int
    row_index: int
    iso_process: Optional[VCSISOProcess] = None
    subprocess: Optional[VCSSubprocess] = None
    stakeholder: Optional[str] = None
    stakeholder_expectations: Optional[str] = None
    stakeholder_needs: List[StakeholderNeedGet] = None


class TableGet(BaseModel):
    table_rows: List[TableRowGet]


# ======================================================================================================================
# VCS Table - Post models
# ======================================================================================================================


class StakeholderNeedPost(BaseModel):
    need: Optional[str] = None
    rank_weight: Optional[int] = 0
    value_driver_ids: Optional[List[int]] = None


class TableRowPost(BaseModel):
    node_id: Optional[int] = None
    row_index: int
    iso_process_id: Optional[int] = None
    subprocess_id: Optional[int] = None
    stakeholder: Optional[str] = None
    stakeholder_expectations: Optional[str] = None
    stakeholder_needs: List[StakeholderNeedPost] = None


class TablePost(BaseModel):
    table_rows: List[TableRowPost]

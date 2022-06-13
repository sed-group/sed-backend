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
# VCS Stakeholder need
# ======================================================================================================================

'''
class VCSStakeholderNeed(BaseModel):
    id: int
    name: str
    rank_weight: int
    vcs_tabel_row: VCSTableRow


class VCSStakeholderNeedPost(BaseModel):
    name: Optional[str] = None
    rank_weight: Optional[int] = None
'''

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
# VCS Table - Representation/return models
# ======================================================================================================================

class VcsRow(BaseModel):
    id: int
    index: int
    stakeholder: str
    stakeholder_needs: str
    stakeholder_expectations: str
    iso_process: Optional[VCSISOProcess] = None
    subprocess: Optional[VCSSubprocess] = None
    value_dimension: Optional[List[int]] = None
    value_drivers: Optional[List[ValueDriver]] = None
    vcs_id: int

class VcsRowPost(BaseModel):
    index: int
    stakeholder: str
    stakeholder_needs: str
    stakeholder_expectations: str
    iso_process: Optional[int] = None
    subprocess: Optional[int] = None
    value_dimension: Optional[List[int]] = None
    value_drivers: Optional[List[int]] = None

"""
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
"""

# ======================================================================================================================
# VCS Table - Post models
# ======================================================================================================================


"""
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
"""

# ======================================================================================================================
# VCS Table Row
# ======================================================================================================================
"""
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
"""

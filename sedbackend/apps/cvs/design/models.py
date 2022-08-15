from typing import Optional, List, Any

from pydantic import BaseModel

from sedbackend.apps.cvs.vcs.models import VCS, ValueDriver, VcsRow
"""
# ======================================================================================================================
# CVS Design Quantified Objectives
# ======================================================================================================================


class QuantifiedObjective(BaseModel):
    design_group: int
    value_driver: ValueDriver
    name: str
    unit: Optional[str] = None


class QuantifiedObjectivePost(BaseModel):
    name: str
    unit: Optional[str] = None


# ======================================================================================================================
# CVS Design Quantified Objectives
# ======================================================================================================================


class QuantifiedObjectiveValue(BaseModel):
    design_id: int
    qo: QuantifiedObjective
    value: float


class QuantifiedObjectiveValuePut(BaseModel):
    design_id: int
    design_group_id: int
    value_driver_id: int
    value: float
"""

# ======================================================================================================================
# CVS Design Groups
# ======================================================================================================================


class DesignGroup(BaseModel):
    id: int
    name: str
    vds: List[ValueDriver]


class DesignGroupPost(BaseModel):
    name: str
    vd_ids: List[int]



# ======================================================================================================================
# CVS Designs
# ======================================================================================================================


class ValueDriverDesignValue(BaseModel):
    vd_id: int
    value: int
    def __eq__(self, other: Any) -> bool:
        return self.vd_id == other.vd_id

class Design(BaseModel):
    id: int
    name: str
    vd_design_values: List[ValueDriverDesignValue]


class DesignPost(BaseModel):
    name: str
    vd_design_values: Optional[List[ValueDriverDesignValue]]

from typing import Optional, List, Any
from pydantic import BaseModel
from sedbackend.apps.cvs.vcs.models import ValueDriver


# ======================================================================================================================
# CVS Design Groups
# ======================================================================================================================


class DesignGroup(BaseModel):
    id: int
    name: str
    vds: List[ValueDriver]


class DesignGroupPut(BaseModel):
    name: str
    vd_ids: Optional[List[int]] = None


class DesignGroupPost(BaseModel):
    name: str
    vcs_id: Optional[int] = None


# ======================================================================================================================
# CVS Designs
# ======================================================================================================================

class ValueDriverDesignValue(BaseModel):
    vd_id: int
    value: float

    def __eq__(self, other: Any) -> bool:
        return self.vd_id == other.vd_id


class Design(BaseModel):
    id: int
    name: str
    design_group_id: Optional[int] = None
    vd_design_values: Optional[List[ValueDriverDesignValue]]


class DesignPut(BaseModel):
    id: Optional[int] = None
    name: str
    vd_design_values: Optional[List[ValueDriverDesignValue]]


class DesignPost(BaseModel):
    name: str
    vd_design_values: Optional[List[ValueDriverDesignValue]]

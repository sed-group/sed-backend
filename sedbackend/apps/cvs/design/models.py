from typing import Optional, List

from pydantic import BaseModel

from sedbackend.apps.cvs.vcs.models import VCS, ValueDriver, VcsRow

# ======================================================================================================================
# CVS Design Quantified Objectives
# ======================================================================================================================


class QuantifiedObjective(BaseModel):
    design_group: int
    value_driver: ValueDriver
    name: str
    unit: str


class QuantifiedObjectivePost(BaseModel):
    name: str
    unit: str


# ======================================================================================================================
# CVS Design Quantified Objectives
# ======================================================================================================================


class QuantifiedObjectiveValue(BaseModel):
    design_id: int  # PRIMARY KEY(`design`, `value_driver`, `design_group`)
    value_driver_id: int
    design_group_id: int
    value: float


class QuantifiedObjectiveValuePost(BaseModel):
    value: float


# ======================================================================================================================
# CVS Design
# ======================================================================================================================


class DesignGroup(BaseModel):
    id: int
    vcs: int
    name: str
    qo_list: List[QuantifiedObjective]


class DesignGroupPost(BaseModel):
    name: str
    qo_list: List[QuantifiedObjective]


# ======================================================================================================================
# CVS Design Row
# ======================================================================================================================


class DesignRow(BaseModel):
    id: int
    design_group: int
    name: str
    qo_values: List[QuantifiedObjectiveValue]


class DesignRowPost(BaseModel):
    name: str
    qo_values: List[QuantifiedObjectiveValuePost]



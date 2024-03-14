from typing import List
from enum import Enum
from pydantic import BaseModel
from typing import Optional
from fastapi import Form

import datetime
from sedbackend.apps.cvs.design.models import DesignGroup, Design, ValueDriverDesignValue
from sedbackend.apps.cvs.link_design_lifecycle import models as link_model
from dataclasses import dataclass

from sedbackend.apps.cvs.vcs.models import VCS, ValueDriver
from sedbackend.apps.cvs.design.models import DesignGroup, Design, ValueDriverDesignValue


class NonTechCost(str, Enum):
    """
    The ways of choosing how to apply the non-technical process costs
    """
    TO_TECHNICAL_PROCESS: str = 'to_process'
    LUMP_SUM: str = 'lump_sum'
    CONTINOUSLY: str = 'continously'
    NO_ADDED_COST: str = 'no_cost'


class Process(BaseModel):
    name: str
    time: float
    cost: float
    revenue: float


class NonTechnicalProcess(BaseModel):
    name: str
    cost: float
    revenue: float


class Simulation(BaseModel):
    time: List[float]
    mean_NPV: List[float]
    max_NPVs: List[float]
    mean_payback_time: float
    all_npvs: List[List[float]]
    payback_time: float
    surplus_value_end_result: float
    design_id: int
    vcs_id: int


class SimulationResult(BaseModel):
    designs: List[Design]
    vcss: List[VCS]
    vds: List[ValueDriver]
    runs: List[Simulation]


class EditSimSettings(BaseModel):
    time_unit: link_model.TimeFormat
    flow_process: Optional[str] = None
    flow_start_time: Optional[float] = None
    flow_time: float
    interarrival_time: float
    start_time: float
    end_time: float
    discount_rate: float
    non_tech_add: NonTechCost
    monte_carlo: bool
    runs: int


class SimSettings(EditSimSettings):
    project: int

class SimulationFetch(BaseModel):
    project_id: int
    file: int
    insert_timestamp: str
    vs_x_ds: str

    

@dataclass
class FileParams:
    time_unit: link_model.TimeFormat = Form(...)
    flow_process: Optional[str] = Form(None)
    flow_start_time: Optional[float] = Form(None)
    flow_time: float = Form(...)
    interarrival_time: float = Form(...)
    start_time: float = Form(...)
    end_time: float = Form(...)
    discount_rate: float = Form(...)
    non_tech_add: NonTechCost = Form(...)
    monte_carlo: bool = Form(...)
    runs: Optional[int] = Form(None)
    vcs_ids: str = Form(...)
    design_ids: str = Form(...)
    normalized_npv: Optional[bool] = Form(None)

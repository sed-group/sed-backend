from typing import List
from enum import Enum
from pydantic import BaseModel
from typing import  Optional
import json
from fastapi import Form
from sedbackend.apps.cvs.link_design_lifecycle import models as link_model
from dataclasses import dataclass


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
    
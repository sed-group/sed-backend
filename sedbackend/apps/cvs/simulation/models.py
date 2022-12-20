from typing import List
from enum import Enum
from pydantic import BaseModel
from typing import  Optional
import json


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


#class Simulation(BaseModel):
    #time: List[float]
    #cumulative_NPV: List[float]
    #processes: List[Process]

class Simulation(BaseModel):
    time: List[float]
    mean_NPV: List[float]
    max_NPVs: List[float]
    mean_payback_time: float
    all_npvs: List[List[float]]


class EditSimSettings(BaseModel):
    time_unit: str
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
    
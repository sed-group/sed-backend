from typing import List
from enum import Enum
from pydantic import BaseModel


class NonTechCost(Enum):
    """
    The ways of choosing how to apply the non-technical process costs
    """
    TO_TECHNICAL_PROCESS = 'to_process'
    LUMP_SUM = 'lump_sum'
    CONTINOUSLY = 'continously'
    NO_ADDED_COST = 'no_cost'


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
    cumulative_NPV: List[float]
    processes: List[Process]

class SimulationMonteCarlo(BaseModel):
    time: List[float]
    mean_NPV: List[float]
    max_NPVs: List[float]
    mean_payback_time: float
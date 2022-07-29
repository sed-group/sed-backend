from typing import List
from enum import Enum
from pydantic import BaseModel


class TimeFormat(Enum):
    """
    The timeformats that can be chosen for a process. The values are the defaults for the
    simulation (years)
    """
    HOUR = 365*24
    DAY = 365
    WEEK = 52
    MONTH = 12
    YEAR = 1


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
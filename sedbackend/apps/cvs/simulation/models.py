from typing import List

from pydantic import BaseModel
from typing import Optional
from sedbackend.apps.cvs.simulation.algorithms import TimeFormat


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
#    surplus_values: List[float]
    cumulative_NPV: List[float]
    processes: List[Process]
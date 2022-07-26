from typing import List

from pydantic import BaseModel


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
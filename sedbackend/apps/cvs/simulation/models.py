from typing import List

from pydantic import BaseModel


class Process(BaseModel):
    name: str
    time: float
    cost: float
    revenue: float


class Simulation(BaseModel):
    time: List[float]
    surplus_values: List[float]
    processes: List[Process]
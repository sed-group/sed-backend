from typing import List, Optional

from pydantic import BaseModel
from sedbackend.apps.cvs.vcs.models import TableRowGet


# ======================================================================================================================
# BPMN Table
# ======================================================================================================================

class NodeGet(BaseModel):
    id: int
    vcs_id: int
    name: str
    node_type: str
    pos_x: Optional[int] = None
    pos_y: Optional[int] = None
    vcs_table_row: Optional[TableRowGet] = None


class NodePost(BaseModel):
    name: str
    node_type: str
    pos_x: Optional[int] = None
    pos_y: Optional[int] = None


class EdgeGet(BaseModel):
    id: int
    vcs_id: int
    name: str
    from_node: int
    to_node: int
    probability: int


class EdgePost(BaseModel):
    name: str
    from_node: int
    to_node: int
    probability: int


class BPMNGet(BaseModel):
    vcs_id: int
    nodes: List[NodeGet]
    edges: List[EdgeGet]


# ======================================================================================================================
# Market Input Table
# ======================================================================================================================

class MarketInputGet(BaseModel):
    id: int
    vcs: int
    node: int
    time: float
    cost: float
    revenue: float


class MarketInputPost(BaseModel):
    time: float
    cost: float
    revenue: float


# ======================================================================================================================
# Simulation
# ======================================================================================================================

class Process(BaseModel):
    name: str
    time: float
    cost: float
    revenue: float


class Simulation(BaseModel):
    time: List[float]
    surplus_values: List[float]
    processes: List[Process]


from typing import Optional, List

from pydantic import BaseModel

from sedbackend.apps.cvs.vcs.models import VcsRow



class NodeGet(BaseModel):
    id: int
    vcs_id: int
    name: str
    node_type: str
    pos_x: Optional[int] = None
    pos_y: Optional[int] = None
    vcs_table_row: Optional[VcsRow] = None


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

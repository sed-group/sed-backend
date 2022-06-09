from typing import List
from pydantic import BaseModel
from sedbackend.apps.cvs.vcs import models as vcs_models


class NodeGet(BaseModel):
    id: int
    vcs_id: int
    pos_x: int
    pos_y: int
    from_node: int
    to_node: int


class NodePost(BaseModel):
    pos_x: int
    pos_y: int


class ProcessNodeGet(NodeGet):
    id: int
    vcs_row: vcs_models.TableRowGet


class StartStopNodeGet(NodeGet):
    type: str


class StartStopNodePost(NodePost):
    type: str


class BPMNGet(BaseModel):
    nodes: List[NodeGet]

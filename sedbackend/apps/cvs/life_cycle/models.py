from typing import List, Optional
from pydantic import BaseModel
from sedbackend.apps.cvs.vcs import models as vcs_models


class NodeGet(BaseModel):
    id: int
    vcs_id: int
    from_node: Optional[int] = None
    to_node: Optional[int] = None
    pos_x: int
    pos_y: int


class NodePost(BaseModel):
    pos_x: int
    pos_y: int


class ProcessNodeGet(NodeGet):
    vcs_row: vcs_models.VcsRow


class ProcessNodePost(NodePost):
    vcs_row: vcs_models.VcsRow


class StartStopNodeGet(NodeGet):
    type: str


class StartStopNodePost(NodePost):
    type: str


class BPMNGet(BaseModel):
    nodes: List[ProcessNodeGet]

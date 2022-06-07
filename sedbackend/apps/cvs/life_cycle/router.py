from typing import List

from fastapi import Depends, APIRouter

from sedbackend.apps.core.authentication.utils import get_current_active_user
from sedbackend.apps.core.users.models import User
from sedbackend.apps.cvs.life_cycle import models, implementation

router = APIRouter()


@router.post(
    '/project/{project_id}/vcs/{vcs_id}/bpmn/node/create',
    summary='Creates a node for BPMN',
    response_model=models.NodeGet,
)
async def create_bpmn_node(node: models.NodePost, project_id: int, vcs_id: int,
                           user: User = Depends(get_current_active_user)) -> models.NodeGet:
    return implementation.create_bpmn_node(node, project_id, vcs_id, user.id)


@router.delete(
    '/project/{project_id}/vcs/{vcs_id}/bpmn/node/{node_id}/delete',
    summary='Deletes a node',
    response_model=bool,
)
async def delete_bpmn_node(node_id: int, project_id: int, vcs_id: int,
                           user: User = Depends(get_current_active_user)) -> bool:
    return implementation.delete_bpmn_node(node_id, project_id, vcs_id, user.id)


@router.put(
    '/project/{project_id}/vcs/{vcs_id}/bpmn/node/{node_id}/edit',
    summary='Edit a node',
    response_model=models.NodeGet,
)
async def update_bpmn_node(node_id: int, node: models.NodePost, project_id: int, vcs_id: int,
                           user: User = Depends(get_current_active_user)) -> models.NodeGet:
    return implementation.update_bpmn_node(node_id, node, project_id, vcs_id, user.id)


@router.post(
    '/project/{project_id}/vcs/{vcs_id}/bpmn/edge/create',
    summary='Creates an edge',
    response_model=models.EdgeGet,
)
async def create_bpmn_edge(edge: models.EdgePost, project_id: int, vcs_id: int,
                           user: User = Depends(get_current_active_user)) -> models.EdgeGet:
    return implementation.create_bpmn_edge(edge, project_id, vcs_id, user.id)


@router.delete(
    '/project/{project_id}/vcs/{vcs_id}/bpmn/edge/{edge_id}/delete',
    summary='Deletes an edge',
    response_model=bool,
)
async def delete_bpmn_edge(edge_id: int, project_id: int, vcs_id: int,
                           user: User = Depends(get_current_active_user)) -> bool:
    return implementation.delete_bpmn_edge(edge_id, project_id, vcs_id, user.id)


@router.put(
    '/project/{project_id}/vcs/{vcs_id}/edge/{edge_id}/edit',
    summary='Edit an edge',
    response_model=models.EdgeGet,
)
async def update_bpmn_edge(edge_id: int, edge: models.EdgePost, project_id: int, vcs_id: int,
                           user: User = Depends(get_current_active_user)) -> models.EdgeGet:
    return implementation.update_bpmn_edge(edge_id, edge, project_id, vcs_id, user.id)


@router.get(
    '/project/{project_id}/vcs/{vcs_id}/bpmn/get',
    summary='Get BPMN',
    response_model=models.BPMNGet,
)
async def get_bpmn(vcs_id: int, project_id: int, user: User = Depends(get_current_active_user)) -> models.BPMNGet:
    return implementation.get_bpmn(vcs_id, project_id, user.id)


@router.put(
    '/project/{project_id}/vcs/{vcs_id}/bpmn/edit',
    summary='Edit BPMN',
    response_model=models.BPMNGet,
)
async def update_bpmn(vcs_id: int, project_id: int, nodes: List[models.NodeGet], edges: List[
    models.EdgeGet],
                      user: User = Depends(get_current_active_user)) -> models.BPMNGet:
    return implementation.update_bpmn(vcs_id, project_id, user.id, nodes, edges)

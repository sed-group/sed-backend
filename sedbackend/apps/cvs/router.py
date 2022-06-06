from fastapi import APIRouter, Depends, Security
from typing import List

from sedbackend.apps.core.users.models import User
from sedbackend.apps.core.authentication.utils import get_current_active_user, verify_token

import sedbackend.apps.cvs.implementation as impl
import sedbackend.apps.cvs.models as models
from sedbackend.apps.cvs.project.router import router as router_project
from sedbackend.apps.cvs.vcs.router import router as router_vcs
from sedbackend.apps.cvs.design.router import router as router_design

router = APIRouter()

CVS_APP_SID = 'MOD.CVS'

router.include_router(router_project, prefix='/project', tags=['cvs project'], dependencies=[Security(verify_token)])
router.include_router(router_vcs, prefix='/vcs', tags=['cvs vcs'], dependencies=[Security(verify_token)])
router.include_router(router_design, prefix='/design', tags=['cvs design'], dependencies=[Security(verify_token)])


# ======================================================================================================================
# BPMN Table
# ======================================================================================================================

@router.post(
    '/project/{project_id}/vcs/{vcs_id}/bpmn/node/create',
    summary='Creates a node for BPMN',
    response_model=models.NodeGet,
)
async def create_bpmn_node(node: models.NodePost, project_id: int, vcs_id: int,
                           user: User = Depends(get_current_active_user)) -> models.NodeGet:
    return impl.create_bpmn_node(node, project_id, vcs_id, user.id)


@router.delete(
    '/project/{project_id}/vcs/{vcs_id}/bpmn/node/{node_id}/delete',
    summary='Deletes a node',
    response_model=bool,
)
async def delete_bpmn_node(node_id: int, project_id: int, vcs_id: int,
                           user: User = Depends(get_current_active_user)) -> bool:
    return impl.delete_bpmn_node(node_id, project_id, vcs_id, user.id)


@router.put(
    '/project/{project_id}/vcs/{vcs_id}/bpmn/node/{node_id}/edit',
    summary='Edit a node',
    response_model=models.NodeGet,
)
async def update_bpmn_node(node_id: int, node: models.NodePost, project_id: int, vcs_id: int,
                           user: User = Depends(get_current_active_user)) -> models.NodeGet:
    return impl.update_bpmn_node(node_id, node, project_id, vcs_id, user.id)


@router.post(
    '/project/{project_id}/vcs/{vcs_id}/bpmn/edge/create',
    summary='Creates an edge',
    response_model=models.EdgeGet,
)
async def create_bpmn_edge(edge: models.EdgePost, project_id: int, vcs_id: int,
                           user: User = Depends(get_current_active_user)) -> models.EdgeGet:
    return impl.create_bpmn_edge(edge, project_id, vcs_id, user.id)


@router.delete(
    '/project/{project_id}/vcs/{vcs_id}/bpmn/edge/{edge_id}/delete',
    summary='Deletes an edge',
    response_model=bool,
)
async def delete_bpmn_edge(edge_id: int, project_id: int, vcs_id: int,
                           user: User = Depends(get_current_active_user)) -> bool:
    return impl.delete_bpmn_edge(edge_id, project_id, vcs_id, user.id)


@router.put(
    '/project/{project_id}/vcs/{vcs_id}/edge/{edge_id}/edit',
    summary='Edit an edge',
    response_model=models.EdgeGet,
)
async def update_bpmn_edge(edge_id: int, edge: models.EdgePost, project_id: int, vcs_id: int,
                           user: User = Depends(get_current_active_user)) -> models.EdgeGet:
    return impl.update_bpmn_edge(edge_id, edge, project_id, vcs_id, user.id)


@router.get(
    '/project/{project_id}/vcs/{vcs_id}/bpmn/get',
    summary='Get BPMN',
    response_model=models.BPMNGet,
)
async def get_bpmn(vcs_id: int, project_id: int, user: User = Depends(get_current_active_user)) -> models.BPMNGet:
    return impl.get_bpmn(vcs_id, project_id, user.id)


@router.put(
    '/project/{project_id}/vcs/{vcs_id}/bpmn/edit',
    summary='Edit BPMN',
    response_model=models.BPMNGet,
)
async def update_bpmn(vcs_id: int, project_id: int, nodes: List[models.NodeGet], edges: List[models.EdgeGet],
                      user: User = Depends(get_current_active_user)) -> models.BPMNGet:
    return impl.update_bpmn(vcs_id, project_id, user.id, nodes, edges)


# ======================================================================================================================
# Market Input Table
# ======================================================================================================================

@router.get(
    '/project/{project_id}/vcs/{vcs_id}/market_input/get/all',
    summary='Get all market inputs',
    response_model=List[models.MarketInputGet],
)
async def get_all_market_input(project_id: int, vcs_id: int,
                               user: User = Depends(get_current_active_user)) -> List[models.MarketInputGet]:
    return impl.get_all_market_inputs(project_id, vcs_id, user.id)


@router.post(
    '/project/{project_id}/vcs/{vcs_id}/bpmn-node/{node_id}/market_input/create',
    summary='Creates a market input',
    response_model=models.MarketInputGet,
)
async def create_market_input(project_id: int, vcs_id: int, node_id: int, market_input: models.MarketInputPost,
                              user: User = Depends(get_current_active_user)) -> models.MarketInputGet:
    return impl.create_market_input(project_id, vcs_id, node_id, market_input, user.id)


@router.put(
    '/project/{project_id}/vcs/{vcs_id}/bpmn-node/{node_id}/market_input/edit',
    summary='Edit market input',
    response_model=models.MarketInputGet,
)
async def update_market_input(project_id: int, vcs_id: int, node_id: int, market_input: models.MarketInputPost,
                              user: User = Depends(get_current_active_user)) -> models.MarketInputGet:
    return impl.update_market_input(project_id, vcs_id, node_id, market_input, user.id)


# ======================================================================================================================
# Simulation
# ======================================================================================================================

@router.get(
    '/project/{project_id}/vcs/{vcs_id}/simulation/run',
    summary='Run simulation',
    response_model=models.Simulation,
)
async def run_simulation(project_id: int, vcs_id: int, time_interval: float,
                         user: User = Depends(get_current_active_user)) -> models.Simulation:
    return impl.run_simulation(project_id, vcs_id, time_interval, user.id)

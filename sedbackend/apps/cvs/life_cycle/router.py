from fastapi import APIRouter, Depends

from sedbackend.apps.core.projects.dependencies import SubProjectAccessChecker
from sedbackend.apps.core.projects.models import AccessLevel
from sedbackend.apps.cvs.life_cycle import models, implementation
from sedbackend.apps.cvs.project.router import CVS_APP_SID

router = APIRouter()


@router.post(
    '/project/{native_project_id}/vcs/{vcs_id}/node/start-stop',
    summary='Creates a start/stop node for BPMN',
    response_model=models.StartStopNodeGet,
    dependencies=[Depends(SubProjectAccessChecker(AccessLevel.list_can_edit(), CVS_APP_SID))]
)
async def create_process_node(node: models.StartStopNodePost, vcs_id: int) -> models.StartStopNodeGet:
    return implementation.create_start_stop_node(node, vcs_id)


@router.delete(
    '/project/{native_project_id}/node/{node_id}',
    summary='Deletes a node',
    response_model=bool,
    dependencies=[Depends(SubProjectAccessChecker(AccessLevel.list_can_edit(), CVS_APP_SID))]
)
async def delete_bpmn_node(native_project_id: int, node_id: int) -> bool:
    return implementation.delete_node(native_project_id, node_id)


@router.put(
    '/project/{native_project_id}/node/{node_id}',
    summary='Edit a node',
    response_model=bool,
    dependencies=[Depends(SubProjectAccessChecker(AccessLevel.list_can_edit(), CVS_APP_SID))]
)
async def update_bpmn_node(native_project_id: int, node_id: int, node: models.NodePost) -> bool:
    return implementation.update_node(native_project_id, node_id, node)


@router.get(
    '/project/{native_project_id}/vcs/{vcs_id}/bpmn',
    summary='Get BPMN',
    response_model=models.BPMNGet,
    dependencies=[Depends(SubProjectAccessChecker(AccessLevel.list_can_read(), CVS_APP_SID))]
)
async def get_bpmn(native_project_id: int, vcs_id: int) -> models.BPMNGet:
    return implementation.get_bpmn(native_project_id, vcs_id)


@router.put(
    '/project/{native_project_id}/vcs/{vcs_id}/bpmn',
    summary='Edit BPMN',
    response_model=bool,
    dependencies=[Depends(SubProjectAccessChecker(AccessLevel.list_can_edit(), CVS_APP_SID))]
)
async def update_bpmn(native_project_id: int, vcs_id: int, bpmn: models.BPMNGet) -> bool:
    return implementation.update_bpmn(native_project_id, vcs_id, bpmn)

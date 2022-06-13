from fastapi import APIRouter

from sedbackend.apps.cvs.life_cycle import models, implementation

router = APIRouter()


@router.post(
    '/vcs/{vcs_id}/bpmn/node/process',
    summary='Creates a process node for BPMN',
    response_model=models.ProcessNodeGet,
)
async def create_process_node(node: models.ProcessNodePost, vcs_id: int) -> models.ProcessNodeGet:
    return implementation.create_process_node(node, vcs_id)


@router.post(
    '/vcs/{vcs_id}/bpmn/node/start_stop',
    summary='Creates a start/stop node for BPMN',
    response_model=models.StartStopNodeGet,
)
async def create_process_node(node: models.StartStopNodePost, vcs_id: int) -> models.StartStopNodeGet:
    return implementation.create_start_stop_node(node, vcs_id)


@router.delete(
    '/vcs/{vcs_id}/bpmn/node/{node_id}',
    summary='Deletes a node',
    response_model=bool,
)
async def delete_bpmn_node(node_id: int, vcs_id: int) -> bool:
    return implementation.delete_node(node_id, vcs_id)


@router.put(
    '/vcs/{vcs_id}/bpmn/node/{node_id}',
    summary='Edit a node',
    response_model=bool,
)
async def update_bpmn_node(node_id: int, node: models.NodePost, vcs_id: int) -> bool:
    return implementation.update_node(node_id, node, vcs_id)


@router.get(
    '/vcs/{vcs_id}/bpmn',
    summary='Get BPMN',
    response_model=models.BPMNGet,
)
async def get_bpmn(vcs_id: int) -> models.BPMNGet:
    return implementation.get_bpmn(vcs_id)


@router.put(
    '/project/{project_id}/vcs/{vcs_id}/bpmn',
    summary='Edit BPMN',
    response_model=bool,
)
async def update_bpmn(vcs_id: int, bpmn: models.BPMNGet) -> bool:
    return implementation.update_bpmn(vcs_id, bpmn)

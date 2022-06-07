from typing import List

from fastapi import Depends, APIRouter

from sedbackend.apps.core.authentication.utils import get_current_active_user
from sedbackend.apps.core.users.models import User
from sedbackend.apps.cvs.market_input import models, implementation

router = APIRouter()

@router.get(
    '/project/{project_id}/vcs/{vcs_id}/market_input/get/all',
    summary='Get all market inputs',
    response_model=List[models.MarketInputGet],
)
async def get_all_market_input(project_id: int, vcs_id: int,
                               user: User = Depends(get_current_active_user)) -> List[models.MarketInputGet]:
    return implementation.get_all_market_inputs(project_id, vcs_id, user.id)


@router.post(
    '/project/{project_id}/vcs/{vcs_id}/bpmn-node/{node_id}/market_input/create',
    summary='Creates a market input',
    response_model=models.MarketInputGet,
)
async def create_market_input(project_id: int, vcs_id: int, node_id: int, market_input: models.MarketInputPost,
                              user: User = Depends(get_current_active_user)) -> models.MarketInputGet:
    return implementation.create_market_input(project_id, vcs_id, node_id, market_input, user.id)


@router.put(
    '/project/{project_id}/vcs/{vcs_id}/bpmn-node/{node_id}/market_input/edit',
    summary='Edit market input',
    response_model=models.MarketInputGet,
)
async def update_market_input(project_id: int, vcs_id: int, node_id: int, market_input: models.MarketInputPost,
                              user: User = Depends(get_current_active_user)) -> models.MarketInputGet:
    return implementation.update_market_input(project_id, vcs_id, node_id, market_input, user.id)

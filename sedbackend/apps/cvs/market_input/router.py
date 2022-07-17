from typing import List

from fastapi import Depends, APIRouter

from sedbackend.apps.core.authentication.utils import get_current_active_user
from sedbackend.apps.core.users.models import User
from sedbackend.apps.cvs.market_input import models, implementation

router = APIRouter()


@router.get(
    '/vcs/{vcs_id}/market-input/all',
    summary='Get all market inputs',
    response_model=List[models.MarketInputGet],
)
async def get_all_market_input(vcs_id: int,
                               user: User = Depends(get_current_active_user)) -> List[models.MarketInputGet]:
    return implementation.get_all_market_inputs(vcs_id, user.id)


@router.post(
    '/bpmn-node/{node_id}/market-input',
    summary='Creates a market input',
    response_model=models.MarketInputGet,
)
async def create_market_input(node_id: int, market_input: models.MarketInputPost) -> models.MarketInputGet:
    return implementation.create_market_input(node_id, market_input)


@router.put(
    '/bpmn-node/{node_id}/market-input/edit',
    summary='Edit market input',
    response_model=models.MarketInputGet,
)
async def update_market_input(node_id: int, market_input: models.MarketInputPost) -> models.MarketInputGet:
    return implementation.update_market_input(node_id, market_input)

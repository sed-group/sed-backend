from typing import List

from fastapi import APIRouter, Depends

from sedbackend.apps.core.authentication.utils import get_current_active_user
from sedbackend.apps.core.users.models import User
from sedbackend.apps.cvs.market_input import models, implementation

router = APIRouter()


########################################################################################################################
# Market Input
########################################################################################################################

@router.get(
    '/project/{project_id}/market-input/all',
    summary='Get all market inputs',
    response_model=List[models.MarketInputGet],
)
async def get_all_market_input(project_id: int) -> List[models.MarketInputGet]:
    return implementation.get_all_market_inputs(project_id)


@router.post(
    '/project/{project_id}/market-input',
    summary='Creates a market input',
    response_model=models.MarketInputGet,
)
async def create_market_input(project_id: int, market_input: models.MarketInputPost) -> models.MarketInputGet:
    return implementation.create_market_input(project_id, market_input)


@router.put(
    '/market-input/{market_input_id}',
    summary='Edit market input',
    response_model=bool,
)
async def update_market_input(market_input_id: int, market_input: models.MarketInputPost) -> bool:
    return implementation.update_market_input(market_input_id, market_input)


@router.delete(
    '/market-input/{market_input_id}',
    summary=f'Delete market input',
    response_model=bool
)
async def delete_market_input(market_input_id: int) -> bool:
    return implementation.delete_market_input(market_input_id)


########################################################################################################################
# Market Values
########################################################################################################################

@router.put(
    '/vcs/{vcs_id}/market-input/{market_input_id}/value',
    summary='Create or update value for a market input',
    response_model=bool
)
async def update_market_value(vcs_id: int, market_input_id: int, value: float,
                              user: User = Depends(get_current_active_user)) -> bool:
    return implementation.update_market_input_value(models.MarketInputValue(
        vcs_id=vcs_id,
        market_input_id=market_input_id,
        value=value),
        user.id
    )


@router.put(
    '/market-input-values',
    summary='Create or update values for market inputs',
    response_model=bool
)
async def update_market_values(mi_values: List[models.MarketInputValue],
                               user: User = Depends(get_current_active_user)) -> bool:
    return implementation.update_market_input_values(mi_values, user.id)


@router.get(
    '/project/{project_id}/market-input/values',
    summary='Fetch all market input values for a project',
    response_model=List[models.MarketInputValue]
)
async def get_all_market_values(project_id: int) -> List[models.MarketInputValue]:
    return implementation.get_all_market_values(project_id)


@router.delete(
    '/vcs/{vcs_id}/market-input/{market_input_id}',
    summary='Delete a market input value',
    response_model=bool
)
async def delete_market_value(vcs_id: int, market_input_id: int) -> bool:
    return implementation.delete_market_value(vcs_id, market_input_id)
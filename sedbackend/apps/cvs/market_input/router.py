from typing import List

from fastapi import APIRouter

from sedbackend.apps.cvs.market_input import models, implementation

router = APIRouter()

#############################################################################################################################
# Market Input
#############################################################################################################################

@router.get(
    '/project/{project_id}/market-input/all',
    summary='Get all market inputs',
    response_model=List[models.MarketInputGet],
)
async def get_all_market_input(project_id: int) -> List[models.MarketInputGet]:
    return implementation.get_all_market_inputs(project_id)


'''
@router.post(
    '/vcs-row/{vcs_row_id}/market-input',
    summary='Creates a market input',
    response_model=bool,
)
async def create_market_input(vcs_row_id: int, market_input: models.MarketInputPost) -> bool:
    return implementation.create_market_input(vcs_row_id, market_input)
'''


@router.put(
    '/project/{project_id}/market-input/{market_input_id}',
    summary='Edit/create market input',
    response_model=bool,
)
async def update_market_input(market_input_id: int, project_id: int, market_input: models.MarketInputPost) -> bool:
    return implementation.update_market_input(market_input_id, project_id, market_input)

@router.delete(
    '/market-input/{market_input_id}',
    summary=f'Delete market input',
    response_model=bool
)
async def delete_market_input(market_input_id: int) -> bool:
    return implementation.delete_market_input(market_input_id)


#############################################################################################################################
# Market Values
#############################################################################################################################

@router.post(
    '/market-input/{market_input_id}/vcs/{vcs_id}',
    summary='Create a new value for a market input',
    response_model=bool
)
async def create_market_value(market_input_id: int, vcs_id: int, value: float) -> bool:
    return implementation.create_market_value(mi_id=market_input_id, vcs_id=vcs_id, value=value)

@router.get(
    '/project/{project_id}/market-input/values/all',
    summary='Fetch all market input values for a project',
    response_model=List[models.MarketValueGet]
)
async def get_all_market_values(project_id: int) -> List[models.MarketValueGet]:
    return implementation.get_all_market_values(project_id)

@router.delete(
    '/vcs/{vcs_id}/market-input/{market_input_id}',
    summary='Delete a market input value',
    response_model=bool
)
async def delete_market_value(vcs_id: int, market_input_id: int) -> bool:
    return implementation.delete_market_value(vcs_id, market_input_id)
from typing import List

from fastapi import APIRouter

from sedbackend.apps.cvs.market_input import models, implementation

router = APIRouter()


@router.get(
    '/vcs/{vcs_id}/market-input/all',
    summary='Get all market inputs',
    response_model=List[models.MarketInputGet],
)
async def get_all_market_input(vcs_id: int) -> List[models.MarketInputGet]:
    return implementation.get_all_market_inputs(vcs_id)

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
    '/vcs-row/{vcs_row_id}/market-input',
    summary='Edit market input',
    response_model=bool,
)
async def update_market_input(vcs_row_id: int, market_input: models.MarketInputPost) -> bool:
    return implementation.update_market_input(vcs_row_id, market_input)

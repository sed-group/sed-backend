from typing import List

from fastapi import APIRouter, Depends

from sedbackend.apps.core.projects.dependencies import SubProjectAccessChecker
from sedbackend.apps.core.projects.models import AccessLevel
from sedbackend.apps.cvs.market_input import models, implementation
from sedbackend.apps.cvs.project.router import CVS_APP_SID

router = APIRouter()


########################################################################################################################
# Market Input
########################################################################################################################

@router.get(
    '/project/{native_project_id}/market-input/all',
    summary='Get all market inputs',
    response_model=List[models.MarketInputGet],
    dependencies=[Depends(SubProjectAccessChecker(AccessLevel.list_can_read(), CVS_APP_SID))]
)
async def get_all_market_input(native_project_id: int) -> List[models.MarketInputGet]:
    return implementation.get_all_market_inputs(native_project_id)


@router.post(
    '/project/{native_project_id}/market-input',
    summary='Creates a market input',
    response_model=models.MarketInputGet,
    dependencies=[Depends(SubProjectAccessChecker(AccessLevel.list_can_edit(), CVS_APP_SID))]
)
async def create_market_input(native_project_id: int, market_input: models.MarketInputPost) -> models.MarketInputGet:
    return implementation.create_market_input(native_project_id, market_input)


@router.put(
    '/project/{native_project_id}/market-input/{market_input_id}',
    summary='Edit market input',
    response_model=bool,
    dependencies=[Depends(SubProjectAccessChecker(AccessLevel.list_can_edit(), CVS_APP_SID))]
)
async def update_market_input(native_project_id: int, market_input_id: int,
                              market_input: models.MarketInputPost) -> bool:
    return implementation.update_market_input(native_project_id, market_input_id, market_input)


@router.delete(
    '/project/{native_project_id}/market-input/{market_input_id}',
    summary=f'Delete market input',
    response_model=bool,
    dependencies=[Depends(SubProjectAccessChecker(AccessLevel.list_can_edit(), CVS_APP_SID))]
)
async def delete_market_input(native_project_id: int, market_input_id: int) -> bool:
    return implementation.delete_market_input(native_project_id, market_input_id)


########################################################################################################################
# Market Values
########################################################################################################################

@router.put(
    '/project/{native_project_id}/vcs/{vcs_id}/market-input/{market_input_id}/value',
    summary='Create or update value for a market input',
    response_model=bool,
    dependencies=[Depends(SubProjectAccessChecker(AccessLevel.list_can_edit(), CVS_APP_SID))]
)
async def update_market_value(native_project_id: int, vcs_id: int, market_input_id: int, value: float) -> bool:
    return implementation.update_market_input_value(native_project_id, models.MarketInputValue(
        vcs_id=vcs_id,
        market_input_id=market_input_id,
        value=value)
    )


@router.put(
    '/project/{native_project_id}/market-input-values',
    summary='Create or update values for market inputs',
    response_model=bool
)
async def update_market_values(native_project_id: int, mi_values: List[models.MarketInputValue]) -> bool:
    return implementation.update_market_input_values(native_project_id, mi_values)


@router.get(
    '/project/{native_project_id}/market-input-values',
    summary='Fetch all market input values for a project',
    response_model=List[models.MarketInputValue]
)
async def get_all_market_values(native_project_id: int) -> List[models.MarketInputValue]:
    return implementation.get_all_market_values(native_project_id)


@router.delete(
    '/project/{native_project_id}/vcs/{vcs_id}/market-input/{market_input_id}',
    summary='Delete a market input value',
    response_model=bool,
    dependencies=[Depends(SubProjectAccessChecker(AccessLevel.list_can_edit(), CVS_APP_SID))]
)
async def delete_market_value(native_project_id: int, vcs_id: int, market_input_id: int) -> bool:
    return implementation.delete_market_value(native_project_id, vcs_id, market_input_id)

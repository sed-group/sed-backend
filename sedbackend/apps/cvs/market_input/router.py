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
    response_model=List[models.ExternalFactor],
    dependencies=[Depends(SubProjectAccessChecker(AccessLevel.list_can_read(), CVS_APP_SID))]
)
async def get_all_market_input(native_project_id: int) -> List[models.ExternalFactor]:
    return implementation.get_all_market_inputs(native_project_id)


@router.post(
    '/project/{native_project_id}/market-input',
    summary='Creates a market input',
    response_model=models.ExternalFactor,
    dependencies=[Depends(SubProjectAccessChecker(AccessLevel.list_can_edit(), CVS_APP_SID))]
)
async def create_market_input(native_project_id: int, market_input: models.ExternalFactorPost) -> models.ExternalFactor:
    return implementation.create_market_input(native_project_id, market_input)


@router.put(
    '/project/{native_project_id}/market-input/{market_input_id}',
    summary='Edit market input',
    response_model=bool,
    dependencies=[Depends(SubProjectAccessChecker(AccessLevel.list_can_edit(), CVS_APP_SID))]
)
async def update_market_input(native_project_id: int, external_factor: models.ExternalFactor) -> bool:
    return implementation.update_external_factor(native_project_id, external_factor)


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
    '/project/{native_project_id}/market-input-values',
    summary='Create or update values for market inputs',
    response_model=bool
)
async def update_market_values(native_project_id: int, mi_values: List[models.ExternalFactorValue]) -> bool:
    return implementation.update_market_input_values(native_project_id, mi_values)


@router.get(
    '/project/{native_project_id}/market-input-values',
    summary='Fetch all market input values for a project',
    response_model=List[models.ExternalFactorValue]
)
async def get_all_market_values(native_project_id: int) -> List[models.ExternalFactorValue]:
    return implementation.get_all_market_values(native_project_id)

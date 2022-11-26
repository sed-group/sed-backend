from typing import List

from fastapi import Depends, APIRouter

from sedbackend.apps.core.projects.dependencies import SubProjectAccessChecker
from sedbackend.apps.core.projects.models import AccessLevel
from sedbackend.apps.cvs.link_design_lifecycle import models, implementation
from sedbackend.apps.cvs.project.router import CVS_APP_SID

router = APIRouter()


@router.post(
    '/project/{native_project_id}/vcs-row/{vcs_row_id}/design-group/{dg_id}/formulas',
    summary='Create formulas for time, cost, and revenue',
    response_model=bool,
    dependencies=[Depends(SubProjectAccessChecker(AccessLevel.list_can_edit(), CVS_APP_SID))]
)
async def create_formulas(native_project_id: int, vcs_row_id: int, dg_id: int, formula: models.FormulaPost) -> bool:
    return implementation.create_formulas(native_project_id, vcs_row_id, dg_id, formula)


@router.get(
    '/project/{native_project_id}/vcs/{vcs_id}/design-group/{dg_id}/formulas/all',
    summary=f'Get all formulas for a single vcs and design group',
    response_model=List[models.FormulaRowGet],
    dependencies=[Depends(SubProjectAccessChecker(AccessLevel.list_can_read(), CVS_APP_SID))]
)
async def get_all_formulas(native_project_id: int, vcs_id: int, dg_id: int) -> List[models.FormulaRowGet]:
    return implementation.get_all_formulas(native_project_id, vcs_id, dg_id)


@router.put(
    '/project/{native_project_id}/vcs-row/{vcs_row_id}/design-group/{dg_id}/formulas',
    summary='Edit or create the formulas for time, cost, and revenue',
    response_model=bool,
    dependencies=[Depends(SubProjectAccessChecker(AccessLevel.list_can_edit(), CVS_APP_SID))]
)
async def edit_formulas(native_project_id: int, vcs_row_id: int, dg_id: int, new_formulas: models.FormulaPost) -> bool:
    return implementation.edit_formulas(native_project_id, vcs_row_id, dg_id, new_formulas)


@router.delete(
    '/project/{native_project_id}/vcs-row/{vcs_row_id}/design-group/{dg_id}/formulas',
    summary=f'Delete time, cost, and revenue formulas',
    response_model=bool,
    dependencies=[Depends(SubProjectAccessChecker(AccessLevel.list_can_edit(), CVS_APP_SID))]
)
async def delete_formulas(native_project_id: int, vcs_row_id: int, dg_id: int) -> bool:
    return implementation.delete_formulas(native_project_id, vcs_row_id, dg_id)


@router.get(
    '/project/{native_project_id}/vcs/design/formula-pairs',
    summary=f'Fetch all finished/unfinished vcs-design pairs',
    response_model=List[models.VcsDgPairs],
    dependencies=[Depends(SubProjectAccessChecker(AccessLevel.list_can_read(), CVS_APP_SID))]
)
async def get_vcs_dg_pairs(native_project_id: int) -> List[models.VcsDgPairs]:
    return implementation.get_vcs_dg_pairs(native_project_id)

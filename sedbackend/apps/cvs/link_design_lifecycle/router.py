from typing import List, Tuple, Optional

from fastapi import Depends, APIRouter

from sedbackend.apps.cvs.link_design_lifecycle import models, implementation

router = APIRouter()

@router.post(
    '/vcs-row/{vcs_row_id}/design-group/{dg_id}/formulas',
    summary='Create formulas for time, cost, and revenue',
    response_model=bool,
)
async def create_formulas(vcs_row_id: int, dg_id: int, formula: models.FormulaPost) -> bool:
    return implementation.create_formulas(vcs_row_id, dg_id, formula)

@router.get(
    '/vcs/{vcs_id}/design-group/{dg_id}/formulas/all',
    summary=f'Get all formulas for a single vcs and design group',
    response_model=List[models.FormulaRowGet]
)
async def get_all_formulas(vcs_id: int, dg_id: int) -> List[models.FormulaRowGet]:
    return implementation.get_all_formulas(vcs_id, dg_id)

@router.put(
    '/vcs-row/{vcs_row_id}/design-group/{dg_id}/formulas',
    summary='Edit or create the formulas for time, cost, and revenue',
    response_model=bool,
)
async def edit_formulas(vcs_row_id: int, dg_id: int, new_formulas: models.FormulaPost) -> bool:
    return implementation.edit_formulas(vcs_row_id, dg_id, new_formulas)

@router.delete(
    '/vcs-row/{vcs_row_id}/design-group/{dg_id}/formulas',
    summary=f'Delete time, cost, and revenue formulas',
    response_model=bool
)
async def delete_formulas(vcs_row_id: int, dg_id: int) -> bool:
    return implementation.delete_formulas(vcs_row_id, dg_id)

@router.get(
    '/project/{project_id}/vcs/design/formula-pairs',
    summary=f'Fetch all finished/unfinished vcs-design pairs',
    response_model=List[models.VcsDgPairs]
)
async def get_vcs_dg_pairs(project_id: int) -> List[models.VcsDgPairs]:
    return implementation.get_vcs_dg_pairs(project_id)
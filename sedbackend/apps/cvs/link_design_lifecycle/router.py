from typing import List

from fastapi import Depends, APIRouter

from sedbackend.apps.cvs.link_design_lifecycle import models, implementation

router = APIRouter()

@router.post(
    '/vcs-row/{vcs_row_id}/formulas',
    summary='Create formulas for time, cost, and revenue',
    response_model=bool,
)
async def create_formulas(vcs_row_id: int, time: str, time_unit: models.TimeFormat, cost: str, revenue: str) -> bool:
    return implementation.create_formulas(vcs_row_id, models.FormulaPost(time=time, time_unit=time_unit, cost=cost, revenue=revenue))

@router.get(
    '/vcs-row/{vcs}/formulas/all',
    summary=f'Get all formulas for a single vcs',
    response_model=List[models.FormulaGet]
)
async def get_all_formulas(vcs_id: int, design_group: int) -> List[models.FormulaRowGet]:
    return implementation.get_all_formulas(vcs_id, design_group)
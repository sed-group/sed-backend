from typing import List

from fastapi import Depends, APIRouter

from sedbackend.apps.cvs.link_design_lifecycle import models, implementation

router = APIRouter()

@router.post(
    '/vcs-row/{vcs_row_id}/formulas',
    summary='Create formulas for time, cost, and revenue',
    response_model=bool,
)
async def create_formulas(vcs_row_id: int, formulas: models.FormulaPost) -> bool:
    return implementation.create_formulas(vcs_row_id, formulas)
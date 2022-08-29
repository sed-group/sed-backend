from typing import List, Tuple

from fastapi import Depends, APIRouter

from sedbackend.apps.cvs.link_design_lifecycle import models, implementation

router = APIRouter()

@router.post(
    '/vcs-row/{vcs_row_id}/design-group/{dg_id}/formulas',
    summary='Create formulas for time, cost, and revenue',
    response_model=bool,
)
async def create_formulas(vcs_row_id: int, dg_id: int, time: str, time_unit: models.TimeFormat, cost: str, revenue: str, 
        rate: models.Rate, value_driver_ids: List[int], market_input_ids: List[int]) -> bool:
    return implementation.create_formulas(vcs_row_id, dg_id, models.FormulaPost(
                                                        time=time, 
                                                        time_unit=time_unit, 
                                                        cost=cost, 
                                                        revenue=revenue, 
                                                        rate=rate,
                                                        value_driver_ids=value_driver_ids,
                                                        market_input_ids=market_input_ids))

@router.get(
    '/vcs/{vcs_id}/design-group/{dg_id}/formulas/all',
    summary=f'Get all formulas for a single vcs and design group',
    response_model=List[models.FormulaRowGet]
)
async def get_all_formulas(vcs_id: int, dg_id: int) -> List[models.FormulaRowGet]:
    return implementation.get_all_formulas(vcs_id, dg_id)

@router.put(
    '/vcs-row/{vcs_row_id}/design-group/{dg_id}/formulas',
    summary='Edit the formulas for time, cost, and revenue',
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
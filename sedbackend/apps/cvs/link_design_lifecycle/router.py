from typing import List, Tuple

from fastapi import Depends, APIRouter

from sedbackend.apps.cvs.link_design_lifecycle import models, implementation

router = APIRouter()

@router.post(
    '/vcs-row/{vcs_row_id}/formulas',
    summary='Create formulas for time, cost, and revenue',
    response_model=bool,
)
async def create_formulas(vcs_row_id: int, time: str, time_unit: models.TimeFormat, cost: str, revenue: str, 
        rate: models.Rate, quantified_objective_ids: List[models.QuantifiedObjectivePost], market_input_ids: List[int]) -> bool:
    return implementation.create_formulas(vcs_row_id, models.FormulaPost(
                                                        time=time, 
                                                        time_unit=time_unit, 
                                                        cost=cost, 
                                                        revenue=revenue, 
                                                        rate=rate,
                                                        quantified_objective_ids=quantified_objective_ids,
                                                        market_input_ids=market_input_ids))

@router.get(
    '/vcs/{vcs_id}/formulas/all',
    summary=f'Get all formulas for a single vcs',
    response_model=List[models.FormulaRowGet]
)
async def get_all_formulas(vcs_id: int) -> List[models.FormulaRowGet]:
    return implementation.get_all_formulas(vcs_id)

@router.put(
    '/vcs-row/{vcs_row_id}/formulas',
    summary='Edit the formulas for time, cost, and revenue',
    response_model=bool,
)
async def edit_formulas(vcs_row_id: int, new_formulas: models.FormulaPost) -> bool:
    return implementation.edit_formulas(vcs_row_id, new_formulas)

@router.delete(
    '/vcs-row/{vcs_row_id}/formulas',
    summary=f'Delete time, cost, and revenue formulas',
    response_model=bool
)
async def delete_formulas(vcs_row_id: int) -> bool:
    return implementation.delete_formulas(vcs_row_id)
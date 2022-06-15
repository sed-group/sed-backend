from typing import List

from fastapi import APIRouter
from sedbackend.apps.cvs.design import models, implementation


router = APIRouter()

# ======================================================================================================================
# CVS Design
# ======================================================================================================================


@router.post(
    '/vcs/{vcs_id}/design',
    summary='Creates a Design',
    response_model=models.Design
)
async def create_design(design_post: models.DesignPost, vcs_id: int) -> models.Design:
    return implementation.create_cvs_design(design_post, vcs_id)


@router.get(
    '/vcs/{vcs_id}/design/all',
    summary='Returns all designs in project and vcs',
    response_model=List[models.Design],
)
async def get_all_designs(vcs_id: int) \
        -> List[models.Design]:
    return implementation.get_all_design(vcs_id)


@router.get(
    '/design/{design_id}',
    summary='Returns a design',
    response_model=models.Design
)
async def get_design(design_id: int) -> models.Design:
    return implementation.get_design(design_id)


@router.delete(
    '/design/{design_id}',
    summary='Deletes a Design based on the design id. Also deletes all associated Quantified Objectives',
    response_model=bool
)
async def delete_design(design_id: int) -> bool:
    return implementation.delete_design(design_id)


@router.put(
    '/design/{design_id}',
    summary='Edit a design',
    response_model=models.Design
)
async def edit_design(design_id: int, design_post: models.DesignPost) -> models.Design:
    return implementation.edit_design(design_id, design_post)


# ======================================================================================================================
# Quantified Objectives
# ======================================================================================================================


@router.get(
    '/design/{design_id}/quantified_objective/all',
    summary='Fetches all quantified objectives for a given design',
    response_model=List[models.QuantifiedObjective]
)
async def get_all_quantified_objectives(design_id: int) -> List[models.QuantifiedObjective]:
    return implementation.get_all_quantified_objectives(design_id)


@router.get(
    '/design/{design_id}/value_driver/{value_driver_id}/quantified_objective',
    summary='Fetches a quantified objective',
    response_model=models.QuantifiedObjective
)
async def get_quantified_objective(value_driver_id: int, design_id: int) -> models.QuantifiedObjective:
    return implementation.get_quantified_objective(value_driver_id, design_id)


@router.delete(
    '/design/{design_id}/value_driver/{value_driver_id}/quantified_objective',
    response_model=bool
)
async def delete_quantified_objective(value_driver_id: int, design_id: int) -> bool:
    return implementation.delete_quantified_objective(value_driver_id, design_id)


@router.put(
    '/design/{design_id}/value_driver/{value_driver_id}/quantified_objective',
    response_model=models.QuantifiedObjective
)
async def edit_quantified_objective(value_driver_id: int, design_id: int,
                                    updated_qo: models.QuantifiedObjectivePost) -> models.QuantifiedObjective:
    return implementation.edit_quantified_objective(value_driver_id, design_id, updated_qo)


@router.post(
    '/design/{design_id}/value_driver/{value_driver_id}/quantified-objective',
    summary='Creates a quantified objective',
    response_model=models.QuantifiedObjective
)
async def create_quantified_objective(quantified_objective_post: models.QuantifiedObjectivePost, design_id: int,
                                      value_driver_id: int) -> models.QuantifiedObjective:
    return implementation.create_quantified_objective(design_id, value_driver_id, quantified_objective_post)

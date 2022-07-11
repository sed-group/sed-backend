from typing import List

from fastapi import APIRouter
from sedbackend.apps.cvs.design import models, implementation


router = APIRouter()

# ======================================================================================================================
# CVS Design
# ======================================================================================================================


@router.post(
    '/vcs/{vcs_id}/design_group',
    summary='Creates a design group',
    response_model=models.DesignGroup
)
async def create_design_group(design_group_post: models.DesignGroupPost, vcs_id: int) -> models.DesignGroup:
    return implementation.create_cvs_design_group(design_group_post, vcs_id)


@router.get(
    '/vcs/{vcs_id}/design_group/all',
    summary='Returns all design group in project and vcs',
    response_model=List[models.DesignGroup],
)
async def get_all_design_groups(vcs_id: int) \
        -> List[models.DesignGroup]:
    return implementation.get_all_design_groups(vcs_id)


@router.get(
    '/design_group/{design_group_id}',
    summary='Returns a design group',
    response_model=models.DesignGroup
)
async def get_design_group(design_group_id: int) -> models.DesignGroup:
    return implementation.get_design_group(design_group_id)


@router.delete(
    '/design_group/{design_group_id}',
    summary='Deletes a design group based on the design group id. Also deletes all associated Quantified Objectives',
    response_model=bool
)
async def delete_design_group(design_group_id: int) -> bool:
    return implementation.delete_design_group(design_group_id)


@router.put(
    '/design_group/{design_group_id}',
    summary='Edit a design group',
    response_model=models.DesignGroup
)
async def edit_design_group(design_group_id: int, design_post: models.DesignGroupPost) -> models.DesignGroup:
    return implementation.edit_design_group(design_group_id, design_post)


# ======================================================================================================================
# Quantified Objectives
# ======================================================================================================================


@router.get(
    '/design_group/{design_group_id}/quantified_objective/all',
    summary='Fetches all quantified objectives for a given design group',
    response_model=List[models.QuantifiedObjective]
)
async def get_all_quantified_objectives(design_group_id: int) -> List[models.QuantifiedObjective]:
    return implementation.get_all_quantified_objectives(design_group_id)


@router.get(
    '/design_group/{design_group_id}/value_driver/{value_driver_id}/quantified_objective',
    summary='Fetches a quantified objective',
    response_model=models.QuantifiedObjective
)
async def get_quantified_objective(value_driver_id: int, design_group_id: int) -> models.QuantifiedObjective:
    return implementation.get_quantified_objective(value_driver_id, design_group_id)


@router.delete(
    '/design_group/{design_group_id}/value_driver/{value_driver_id}/quantified_objective',
    response_model=bool
)
async def delete_quantified_objective(value_driver_id: int, design_group_id: int) -> bool:
    return implementation.delete_quantified_objective(value_driver_id, design_group_id)


@router.put(
    '/design_group/{design_group_id}/value_driver/{value_driver_id}/quantified_objective',
    response_model=models.QuantifiedObjective
)
async def edit_quantified_objective(value_driver_id: int, design_group_id: int,
                                    updated_qo: models.QuantifiedObjectivePost) -> models.QuantifiedObjective:
    return implementation.edit_quantified_objective(value_driver_id, design_group_id, updated_qo)


@router.post(
    '/design_group/{design_group_id}/value_driver/{value_driver_id}/quantified-objective',
    summary='Creates a quantified objective',
    response_model=bool
)
async def create_quantified_objective(quantified_objective_post: models.QuantifiedObjectivePost, design_group_id: int,
                                      value_driver_id: int) -> bool:
    return implementation.create_quantified_objective(design_group_id, value_driver_id, quantified_objective_post)

from typing import List

from fastapi import APIRouter
from sedbackend.apps.cvs.design import models, implementation


router = APIRouter()

# ======================================================================================================================
# CVS Design Group
# ======================================================================================================================


@router.post(
    '/vcs/{vcs_id}/design-group',
    summary='Creates a design group',
    response_model=models.DesignGroup
)
async def create_design_group(design_group_post: models.DesignGroupPost, vcs_id: int) -> models.DesignGroup:
    return implementation.create_cvs_design_group(design_group_post, vcs_id)


@router.get(
    '/vcs/{vcs_id}/design-group/all',
    summary='Returns all design group in project and vcs',
    response_model=List[models.DesignGroup],
)
async def get_all_design_groups(vcs_id: int) \
        -> List[models.DesignGroup]:
    return implementation.get_all_design_groups(vcs_id)


@router.get(
    '/design-group/{design_group_id}',
    summary='Returns a design group',
    response_model=models.DesignGroup
)
async def get_design_group(design_group_id: int) -> models.DesignGroup:
    return implementation.get_design_group(design_group_id)


@router.delete(
    '/design-group/{design_group_id}',
    summary='Deletes a design group based on the design group id. Also deletes all associated Quantified Objectives',
    response_model=bool
)
async def delete_design_group(design_group_id: int) -> bool:
    return implementation.delete_design_group(design_group_id)


@router.put(
    '/design-group/{design_group_id}',
    summary='Edit a design group',
    response_model=models.DesignGroup
)
async def edit_design_group(design_group_id: int, design_post: models.DesignGroupPost) -> models.DesignGroup:
    return implementation.edit_design_group(design_group_id, design_post)


# ======================================================================================================================
# CVS Design Group
# ======================================================================================================================

@router.get(
    '/design/{design_id}',
    summary='Get design',
    response_model=models.Design
)
async def get_design(design_id: int) -> models.Design:
    return implementation.get_design(design_id)


@router.get(
    '/design-group/{design_group_id}/design/all',
    summary='Get all designs',
    response_model=List[models.Design]
)
async def get_all_designs(design_group_id: int) -> List[models.Design]:
    return implementation.get_all_designs(design_group_id)


@router.post(
    '/design-group/{design_group_id}/design',
    summary='Create design',
    response_model=bool
)
async def create_design(design_group_id: int, design: models.DesignPost) -> bool:
    return implementation.create_design(design_group_id, design)


@router.put(
    '/design/{design_id}',
    summary='Edit design',
    response_model=bool
)
async def edit_design(design_id: int, design: models.DesignPost) -> bool:
    return implementation.edit_design(design_id, design)


@router.delete(
    '/design/{design_id}',
    summary='Delete design',
    response_model=bool
)
async def delete_design(design_id: int) -> bool:
    return implementation.delete_design(design_id)


# ======================================================================================================================
# Quantified Objectives
# ======================================================================================================================


@router.get(
    '/design-group/{design_group_id}/quantified-objective/all',
    summary='Fetches all quantified objectives for a given design group',
    response_model=List[models.QuantifiedObjective]
)
async def get_all_quantified_objectives(design_group_id: int) -> List[models.QuantifiedObjective]:
    return implementation.get_all_quantified_objectives(design_group_id)


@router.get(
    '/design-group/{design_group_id}/value-driver/{value_driver_id}/quantified-objective',
    summary='Fetches a quantified objective',
    response_model=models.QuantifiedObjective
)
async def get_quantified_objective(value_driver_id: int, design_group_id: int) -> models.QuantifiedObjective:
    return implementation.get_quantified_objective(value_driver_id, design_group_id)


@router.delete(
    '/design-group/{design_group_id}/value-driver/{value_driver_id}/quantified-objective',
    response_model=bool
)
async def delete_quantified_objective(value_driver_id: int, design_group_id: int) -> bool:
    return implementation.delete_quantified_objective(value_driver_id, design_group_id)


@router.put(
    '/design-group/{design_group_id}/value-driver/{value_driver_id}/quantified-objective',
    response_model=models.QuantifiedObjective
)
async def edit_quantified_objective(value_driver_id: int, design_group_id: int,
                                    updated_qo: models.QuantifiedObjectivePost) -> models.QuantifiedObjective:
    return implementation.edit_quantified_objective(value_driver_id, design_group_id, updated_qo)


@router.post(
    '/design-group/{design_group_id}/value-driver/{value_driver_id}/quantified-objective',
    summary='Creates a quantified objective',
    response_model=bool
)
async def create_quantified_objective(quantified_objective_post: models.QuantifiedObjectivePost, design_group_id: int,
                                      value_driver_id: int) -> bool:
    return implementation.create_quantified_objective(design_group_id, value_driver_id, quantified_objective_post)


@router.post(
    '/quantified-objective/value',
    summary='Create a value for a quantified objective',
    response_model=models.QuantifiedObjectiveValue
)
async def create_qo_value(design_group_id: int, design_id: int, value_driver_id: int, value: float) -> models.QuantifiedObjectiveValue:
    return implementation.create_qo_value(design_group_id, design_id, value_driver_id, value)

@router.put(
    '/quantified-objective/value',
    summary='Edit a value for a quantified objective',
    response_model=models.QuantifiedObjectiveValue
)
async def edit_qo_value(design_group_id: int, design_id: int, value_driver_id: int,
                  value: float) -> models.QuantifiedObjectiveValue:
    return implementation.edit_qo_value(design_group_id, design_id, value_driver_id, value)

@router.get(
    '/design/{design_id}/quantified-objective/all',
    summary='Fetch all quantified objective values for a single design',
    response_model=List[models.QuantifiedObjectiveValue]
)
async def get_all_qo_values(design_id: int) -> List[models.QuantifiedObjectiveValue]:
    return implementation.get_all_qo_values(design_id)
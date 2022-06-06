from typing import List

from fastapi import Depends, APIRouter

from sedbackend.apps.core.authentication.utils import get_current_active_user
from sedbackend.apps.core.users.models import User
from sedbackend.libs.datastructures.pagination import ListChunk
from sedbackend.apps.cvs.design import models, implementation


router = APIRouter()

# ======================================================================================================================
# CVS Design
# ======================================================================================================================


@router.post(
    '/project/{project_id}/vcs/{vcs_id}/design/create',
    summary='Creates a Design',
    response_model=models.Design
)
async def create_design(design_post: models.DesignPost, vcs_id: int, project_id: int,
                        user: User = Depends(get_current_active_user)) -> models.Design:
    return implementation.create_cvs_design(design_post, vcs_id, project_id, user.id)


@router.get(
    '/project/{project_id}/vcs/{vcs_id}/design/get/all',
    summary='Returns all designs in project and vcs',
    response_model=ListChunk[models.Design],
)
async def get_all_designs(project_id: int, vcs_id: int, user: User = Depends(get_current_active_user)) \
        -> ListChunk[models.Design]:
    return implementation.get_all_design(project_id, vcs_id, user.id)


@router.get(
    '/project/{project_id}/vcs/{vcs_id}/design/get/{design_id}',
    summary='Returns a design',
    response_model=models.Design
)
async def get_design(design_id: int, vcs_id: int, project_id: int,
                     user: User = Depends(get_current_active_user)) -> models.Design:
    return implementation.get_design(design_id, vcs_id, project_id, user.id)


@router.delete(
    '/project/{project_id}/vcs/{vcs_id}/design/{design_id}/delete',
    summary='Deletes a Design based on the design id. Also deletes all associated Quantified Objectives',
    response_model=bool
)
async def delete_design(design_id: int, project_id: int, vcs_id: int,
                        user: User = Depends(get_current_active_user)) -> bool:
    return implementation.delete_design(design_id, vcs_id, project_id, user.id)


@router.put(
    '/project/{project_id}/vcs/{vcs_id}/design/{design_id}/edit',
    summary='Edit a design',
    response_model=models.Design
)
async def edit_design(design_id: int, project_id: int, vcs_id: int, design_post: models.DesignPost,
                      user: User = Depends(get_current_active_user)) -> models.Design:
    return implementation.edit_design(design_id, project_id, vcs_id, user.id, design_post)


# ======================================================================================================================
# Quantified Objectives
# ======================================================================================================================


@router.get(
    '/project/{project_id}/vcs/{vcs_id}/design/{design_id}/quantified_objective/get/all',
    summary='Fetches all quantified objectives for a given design',
    response_model=List[models.QuantifiedObjective]
)
async def get_all_quantified_objectives(project_id: int, vcs_id: int, design_id: int,
                                        user: User = Depends(get_current_active_user)) \
        -> List[models.QuantifiedObjective]:
    return implementation.get_all_quantified_objectives(design_id, project_id, vcs_id, user.id)


@router.get(
    '/project/{project_id}/vcs/{vcs_id}/design/{design_id}/value_driver/{value_driver_id}/quantified_objective/get/{qo_id}',
    summary='Fetches a quantified objective',
    response_model=models.QuantifiedObjective
)
async def get_quantified_objective(qo_id: int, design_id: int, value_driver_id: int,
                                   project_id: int, vcs_id: int,
                                   user: User = Depends(get_current_active_user)) -> models.QuantifiedObjective:
    return implementation.get_quantified_objective(qo_id, design_id, value_driver_id, project_id, vcs_id, user.id)


@router.delete(
    '/project/{project_id}/vcs/{vcs_id}/design/{design_id}/value_driver/{value_driver_id}/quantified-objective/{qo_id}/delete',
    response_model=bool
)
async def delete_quantified_objective(qo_id: int, design_id: int, value_driver_id: int, project_id: int, vcs_id: int,
                                      user: User = Depends(get_current_active_user)) -> bool:
    return implementation.delete_quantified_objective(qo_id, value_driver_id, design_id, project_id, vcs_id, user.id)


@router.put(
    '/project/{project_id}/vcs/{vcs_id}/design/{design_id}/value_driver/{value_driver_id}/quantified-objective/{qo_id}/edit',
    response_model=models.QuantifiedObjective
)
async def edit_quantified_objective(project_id: int, vcs_id: int, design_id: int, value_driver_id: int, qo_id: int,
                                    updated_qo: models.QuantifiedObjectivePost,
                                    user: User = Depends(get_current_active_user)) -> models.QuantifiedObjective:
    return implementation.edit_quantified_objective(qo_id, design_id, value_driver_id, project_id, vcs_id, updated_qo, user.id)


@router.post(
    '/project/{project_id}/vcs/{vcs_id}/design/{design_id}/value_driver/{value_driver_id}/quantified-objective/create',
    summary='Creates a quantified objective',
    response_model=models.QuantifiedObjective
)
async def create_quantified_objective(quantified_objective_post: models.QuantifiedObjectivePost, design_id: int,
                                      project_id: int, vcs_id: int, value_driver_id: int,
                                      user: User = Depends(get_current_active_user)) -> models.QuantifiedObjective:
    return implementation.create_quantified_objective(design_id, value_driver_id, quantified_objective_post,
                                                      project_id, vcs_id, user.id)

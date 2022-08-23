from typing import List

from fastapi import APIRouter
from sedbackend.apps.cvs.design import models, implementation
from sedbackend.apps.cvs.vcs.models import ValueDriver
from sedbackend.apps.cvs.vcs import implementation as vcs_impl


router = APIRouter()

# ======================================================================================================================
# CVS Design Group
# ======================================================================================================================


@router.post(
    '/project/{project_id}/design-group',
    summary='Creates a design group in a project',
    response_model=models.DesignGroup
)
async def create_design_group(design_group_post: models.DesignGroupPost, project_id: int) \
        -> models.DesignGroup:
    return implementation.create_cvs_design_group(design_group_post, project_id)


@router.get(
    '/project/{project_id}/design-group/all',
    summary='Returns all design groups in a project',
    response_model=List[models.DesignGroup],
)
async def get_all_design_groups(project_id: int) \
        -> List[models.DesignGroup]:
    return implementation.get_all_design_groups(project_id)


@router.get(
    '/vcs/{vcs}/value-driver/all',
    summary='Fetch all value drivers in a vcs',
    response_model=List[ValueDriver]
)
async def get_all_value_driver_vcs(vcs_id: int) -> List[ValueDriver]:
    return vcs_impl.get_all_value_driver_vcs(vcs_id)


@router.get(
    '/design-group/{design_group_id}',
    summary='Returns a design group',
    response_model=models.DesignGroup
)
async def get_design_group(design_group_id: int) -> models.DesignGroup:
    return implementation.get_design_group(design_group_id)


@router.delete(
    '/design-group/{design_group_id}',
    summary='Deletes a design group based on the design group id. Also deletes all associated designs and their vd values',
    response_model=bool
)
async def delete_design_group(design_group_id: int) -> bool:
    return implementation.delete_design_group(design_group_id)


@router.put(
    '/design-group/{design_group_id}',
    summary='Edit a design group',
    response_model=models.DesignGroup
)
async def edit_design_group(design_group_id: int, design_group: models.DesignGroupPut) -> models.DesignGroup:
    return implementation.edit_design_group(design_group_id, design_group)


# ======================================================================================================================
# CVS Design 
# ======================================================================================================================
"""
@router.get(
    '/design/{design_id}',
    summary='Get design',
    response_model=models.Design
)
async def get_design(design_id: int) -> models.Design:
    return implementation.get_design(design_id)
"""

@router.get(
    '/design-group/{design_group_id}/design/all',
    summary='Get all designs',
    response_model=List[models.Design]
)
async def get_all_designs(design_group_id: int) -> List[models.Design]:
    return implementation.get_all_designs(design_group_id)


@router.put(
    '/design-group/{design_group_id}/designs',
    summary='Edit designs',
    response_model=bool
)
async def edit_design(design_group_id: int, designs: List[models.DesignPut]) -> bool:
    return implementation.edit_designs(design_group_id, designs)



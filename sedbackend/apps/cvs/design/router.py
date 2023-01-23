from typing import List

from fastapi import APIRouter, Depends

from sedbackend.apps.core.projects.dependencies import SubProjectAccessChecker
from sedbackend.apps.core.projects.models import AccessLevel
from sedbackend.apps.cvs.design import models, implementation
from sedbackend.apps.cvs.project.router import CVS_APP_SID

router = APIRouter()


# ======================================================================================================================
# CVS Design Group
# ======================================================================================================================


@router.post(
    '/project/{native_project_id}/design-group',
    summary='Creates a design group in a project',
    response_model=models.DesignGroup,
    dependencies=[Depends(SubProjectAccessChecker(AccessLevel.list_can_edit(), CVS_APP_SID))]
)
async def create_design_group(native_project_id: int, design_group_post: models.DesignGroupPost) \
        -> models.DesignGroup:
    return implementation.create_cvs_design_group(native_project_id, design_group_post)


@router.get(
    '/project/{native_project_id}/design-group/all',
    summary='Returns all design groups in a project',
    response_model=List[models.DesignGroup],
    dependencies=[Depends(SubProjectAccessChecker(AccessLevel.list_can_read(), CVS_APP_SID))]
)
async def get_all_design_groups(native_project_id: int) \
        -> List[models.DesignGroup]:
    return implementation.get_all_design_groups(native_project_id)


@router.get(
    '/project/{native_project_id}/design-group/{design_group_id}',
    summary='Returns a design group',
    response_model=models.DesignGroup,
    dependencies=[Depends(SubProjectAccessChecker(AccessLevel.list_can_read(), CVS_APP_SID))]
)
async def get_design_group(native_project_id: int, design_group_id: int) -> models.DesignGroup:
    return implementation.get_design_group(native_project_id, design_group_id)


@router.delete(
    '/project/{native_project_id}/design-group/{design_group_id}',
    summary='Deletes a design group based on the design group id. '
            'Also deletes all associated designs and their vd values',
    response_model=bool,
    dependencies=[Depends(SubProjectAccessChecker(AccessLevel.list_can_edit(), CVS_APP_SID))]
)
async def delete_design_group(native_project_id: int, design_group_id: int) -> bool:
    return implementation.delete_design_group(native_project_id, design_group_id)


@router.put(
    '/project/{native_project_id}/design-group/{design_group_id}',
    summary='Edit a design group',
    response_model=models.DesignGroup,
    dependencies=[Depends(SubProjectAccessChecker(AccessLevel.list_can_edit(), CVS_APP_SID))]
)
async def edit_design_group(native_project_id: int, design_group_id: int,
                            design_group: models.DesignGroupPut) -> models.DesignGroup:
    return implementation.edit_design_group(native_project_id, design_group_id, design_group)


# ======================================================================================================================
# CVS Design 
# ======================================================================================================================

@router.get(
    '/project/{native_project_id}/design-group/{design_group_id}/design/all',
    summary='Get all designs',
    response_model=List[models.Design],
    dependencies=[Depends(SubProjectAccessChecker(AccessLevel.list_can_read(), CVS_APP_SID))]
)
async def get_all_designs(native_project_id: int, design_group_id: int) -> List[models.Design]:
    return implementation.get_all_designs(native_project_id, design_group_id)


@router.put(
    '/project/{native_project_id}/design-group/{design_group_id}/designs',
    summary='Edit designs',
    response_model=bool,
    dependencies=[Depends(SubProjectAccessChecker(AccessLevel.list_can_edit(), CVS_APP_SID))]
)
async def edit_design(native_project_id: int, design_group_id: int, designs: List[models.DesignPut]) -> bool:
    return implementation.edit_designs(native_project_id, design_group_id, designs)

from fastapi import APIRouter, Depends

import sedbackend.apps.difam.implementation as impl
import sedbackend.apps.difam.models as models
from libs.datastructures.pagination import ListChunk
from sedbackend.apps.core.users.models import User
from sedbackend.apps.core.authentication.utils import get_current_active_user
from sedbackend.apps.core.projects.dependencies import SubProjectAccessChecker
from sedbackend.apps.core.projects.models import AccessLevel

router = APIRouter()

DIFAM_APP_SID = 'MOD.DIFAM'


@router.get("/projects/",
            summary="List available DIFAM projects",
            response_model=ListChunk[models.DifamProject])
async def get_difam_projects(segment_length: int, index: int, current_user: User = Depends(get_current_active_user)) \
        -> ListChunk[models.DifamProject]:
    current_user_id = current_user.id
    return impl.impl_get_difam_projects(segment_length, index, current_user_id)


@router.get("/projects/{native_project_id}",
            summary="Returns overview of DIFAM project",
            description="Returns overview of DIFAM project",
            response_model=models.DifamProject,
            dependencies=[Depends(SubProjectAccessChecker(AccessLevel.list_can_read(), DIFAM_APP_SID))])
async def get_difam_project(native_project_id: int) -> models.DifamProject:
    """
    Returns overview difam project information
    """
    return impl.impl_get_difam_project(native_project_id)


@router.post("/projects/",
             summary="Create new DIFAM project",
             response_model=models.DifamProject)
async def post_difam_project(difam_project_post: models.DifamProjectPost,
                             current_user: User = Depends(get_current_active_user)) -> models.DifamProject:
    current_user_id = current_user.id
    return impl.impl_post_difam_project(difam_project_post, current_user_id)


@router.put("/projects/{native_project_id}/archetype",
            summary="Set archetype",
            response_model=models.DifamProject,
            dependencies=[Depends(SubProjectAccessChecker(AccessLevel.list_are_admins(), DIFAM_APP_SID))])
async def put_difam_archetype(native_project_id: int, individual_archetype_id: int):
    return impl.impl_put_project_archetype(native_project_id, individual_archetype_id)


@router.post("/projects/{native_project_id}/generate/doe",
             summary="Generate individuals based on design of experiments request",
             dependencies=[Depends(SubProjectAccessChecker(AccessLevel.list_can_edit(), DIFAM_APP_SID))])
async def post_generate_individuals(native_project_id: int, individual_archetype_id: int,
                                    doe_generation_request: models.DOEGenerationRequest,
                                    current_user: User = Depends(get_current_active_user)):
    current_user_id = current_user.id
    return impl.impl_post_generate_individuals(individual_archetype_id, doe_generation_request, current_user_id)


@router.delete("/projects/{native_project_id}",
               summary="Delete DIFAM project",
               response_model=bool,
               dependencies=[Depends(SubProjectAccessChecker(AccessLevel.list_are_admins(), DIFAM_APP_SID))])
async def delete_difam_project(native_project_id: int,
                               current_user: User = Depends(get_current_active_user)):
    current_user_id = current_user.id
    return impl.impl_delete_project(native_project_id, current_user_id)

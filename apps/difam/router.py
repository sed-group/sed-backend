from typing import List

from fastapi import APIRouter, Security, Depends

import apps.difam.implementation as impl
import apps.difam.models as models
from libs.datastructures.pagination import ListChunk
from apps.core.users.models import User
from apps.core.authentication.utils import get_current_active_user

router = APIRouter()


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
            response_model=models.DifamProject)
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
            response_model=models.DifamProject)
async def put_difam_archetype(native_project_id: int, individual_archetype_id: int):
    return impl.impl_put_project_archetype(native_project_id, individual_archetype_id)


@router.delete("/projects/{native_project_id}",
               summary="Delete DIFAM project",
               response_model=bool)
async def delete_difam_project(native_project_id: int,
                               current_user: User = Depends(get_current_active_user)):
    current_user_id = current_user.id
    return impl.impl_delete_project(native_project_id, current_user_id)

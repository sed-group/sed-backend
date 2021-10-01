from libs.datastructures.pagination import ListChunk

from fastapi import APIRouter, Depends

from apps.core.users.models import User
from apps.core.authentication.utils import get_current_active_user
from apps.core.projects.dependencies import SubProjectAccessChecker
from apps.core.projects.models import AccessLevel

import apps.cvs.implementation as impl
import apps.cvs.models as models

router = APIRouter()

CVS_APP_SID = 'MOD.CVS'


@router.get(
    '/projects/all/',
    summary='Returns all of the user\'s CVS projects',
    response_model=ListChunk[models.CVSProject],
)
async def get_difam_projects(segment_length: int, index: int, user: User = Depends(get_current_active_user)) \
        -> ListChunk[models.CVSProject]:
    return impl.get_cvs_projects(segment_length, index, user.id)


@router.get(
    '/projects/{project_id}/',
    summary='Returns a CVS project based on id',
    description='Returns a CVS project based on id',
    response_model=models.CVSProject,
)
async def get_difam_project(project_id: int) -> models.CVSProject:
    return impl.get_cvs_project(project_id)


@router.post(
    '/projects/create/',
    summary='Creates a new CVS project',
    response_model=models.CVSProject,
)
async def post_difam_project(project_post: models.CVSProjectPost,
                             user: User = Depends(get_current_active_user)) -> models.CVSProject:
    return impl.create_cvs_project(project_post, user.id)


@router.delete(
    '/projects/{project_id}/delete',
    summary='Deletes a CVS project based on id',
    response_model=bool,
)
async def delete_cvs_project(project_id: int, user: User = Depends(get_current_active_user)):
    return impl.delete_cvs_project(project_id, user.id)

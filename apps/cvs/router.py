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
async def get_cvs_projects(segment_length: int, index: int, user: User = Depends(get_current_active_user)) \
        -> ListChunk[models.CVSProject]:
    return impl.get_cvs_projects(segment_length, index, user.id)


@router.get(
    '/project/get/{project_id}/',
    summary='Returns a CVS project based on id',
    description='Returns a CVS project based on id',
    response_model=models.CVSProject,
)
async def get_csv_project(project_id: int, user: User = Depends(get_current_active_user)) -> models.CVSProject:
    return impl.get_cvs_project(project_id, user.id)


@router.post(
    '/project/create/',
    summary='Creates a new CVS project',
    response_model=models.CVSProject,
)
async def create_csv_project(project_post: models.CVSProjectPost,
                             user: User = Depends(get_current_active_user)) -> models.CVSProject:
    return impl.create_cvs_project(project_post, user.id)


@router.put(
    '/project/{project_id}/edit/',
    summary='Edits a CVS project',
    response_model=models.CVSProject,
)
async def edit_csv_project(project_id: int, project_post: models.CVSProjectPost,
                           user: User = Depends(get_current_active_user)) -> models.CVSProject:
    return impl.edit_cvs_project(project_id=project_id, user_id=user.id, project_post=project_post)


@router.delete(
    '/project/{project_id}/delete/',
    summary='Deletes a CVS project based on id',
    response_model=bool,
)
async def delete_cvs_project(project_id: int, user: User = Depends(get_current_active_user)):
    return impl.delete_cvs_project(project_id, user.id)

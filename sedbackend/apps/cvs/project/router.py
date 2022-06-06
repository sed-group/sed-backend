from fastapi import Depends, APIRouter

import sedbackend.apps
from sedbackend.apps.core.authentication.utils import get_current_active_user
from sedbackend.apps.core.users.models import User
from sedbackend.libs.datastructures.pagination import ListChunk
from sedbackend.apps.cvs.project import models, implementation


router = APIRouter()

@router.get(
    '/project/get/all',
    summary='Returns all of the user\'s CVS projects',
    response_model=ListChunk[models.CVSProject],
)
async def get_all_cvs_project(user: User = Depends(get_current_active_user)) \
        -> ListChunk[models.CVSProject]:
    return implementation.get_all_cvs_project(user.id)


@router.get(
    '/project/get/segment',
    summary='Returns a segment of the user\'s CVS projects',
    response_model=ListChunk[models.CVSProject],
)
async def get_segment_cvs_project(index: int, segment_length: int, user: User = Depends(get_current_active_user)) \
        -> ListChunk[models.CVSProject]:
    return implementation.get_segment_cvs_project(index, segment_length, user.id)


@router.get(
    '/project/get/{project_id}',
    summary='Returns a CVS project based on id',
    description='Returns a CVS project based on id',
    response_model=models.CVSProject,
)
async def get_csv_project(project_id: int, user: User = Depends(get_current_active_user)) -> models.CVSProject:
    return implementation.get_cvs_project(project_id, user.id)


@router.post(
    '/project/create',
    summary='Creates a new CVS project',
    response_model=models.CVSProject,
)
async def create_csv_project(project_post: models.CVSProjectPost,
                             user: User = Depends(get_current_active_user)) -> models.CVSProject:
    return implementation.create_cvs_project(project_post, user.id)


@router.put(
    '/project/{project_id}/edit',
    summary='Edits a CVS project',
    response_model=models.CVSProject,
)
async def edit_csv_project(project_id: int, project_post: models.CVSProjectPost,
                           user: User = Depends(get_current_active_user)) -> models.CVSProject:
    return implementation.edit_cvs_project(project_id=project_id, user_id=user.id, project_post=project_post)


@router.delete(
    '/project/{project_id}/delete',
    summary='Deletes a CVS project based on id',
    response_model=bool,
)
async def delete_cvs_project(project_id: int, user: User = Depends(get_current_active_user)) -> bool:
    return implementation.delete_cvs_project(project_id, user.id)

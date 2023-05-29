from typing import List, Optional

from fastapi import APIRouter, Security, Depends

import sedbackend.apps.core.projects.implementation as impl
from sedbackend.apps.core.projects.dependencies import ProjectAccessChecker
from sedbackend.apps.core.authentication.utils import verify_scopes, get_current_active_user
import sedbackend.apps.core.projects.models as models
from sedbackend.apps.core.users.models import User


router = APIRouter()


@router.get("",
            summary="Lists all accessible projects",
            description="Lists all projects in alphabetical order",
            response_model=List[models.ProjectListing])
async def get_projects(segment_length: Optional[int] = 0, index: Optional[int] = 0,
                       current_user: User = Depends(get_current_active_user)):
    """
    Lists all projects that the current user has access to
    :param current_user:
    :param segment_length:
    :param index:
    :return:
    """
    return impl.impl_get_user_projects(current_user.id, segment_length=segment_length, index=index)


@router.get("/all",
            summary="Get all projects",
            description="Lists all projects that exist, and is only available to those who have the authority.",
            response_model=List[models.ProjectListing],
            dependencies=[Security(verify_scopes, scopes=['admin'])])
async def get_all_projects(segment_length: Optional[int] = 0, index: Optional[int] = 0,
                           current_user: User = Depends(get_current_active_user)):
    """
    Lists all projects that exists, and is only available to those who have the authority.
    :param current_user:
    :param segment_length:
    :param index:
    :return:
    """
    return impl.impl_get_projects(current_user.id, segment_length, index)


@router.get("/{project_id}",
            summary="Get project",
            response_model=models.Project,
            description="Get a specific project using project ID",
            dependencies=[Depends(ProjectAccessChecker(models.AccessLevel.list_can_read()))])
async def get_project(project_id: int):
    return impl.impl_get_project(project_id)


@router.post("",
             summary="Create project",
             description="Create a new empty project. The current user is automatically set as the owner.",
             response_model=models.Project,
             dependencies=[Security(verify_scopes, scopes=['admin'])])
async def post_project(project: models.ProjectPost, current_user: User = Depends(get_current_active_user)):
    current_user_id = current_user.id
    return impl.impl_post_project(project, current_user_id)


@router.delete("/{project_id}",
               summary="Delete project",
               description="Delete a project",
               response_model=bool,
               dependencies=[Depends(ProjectAccessChecker([models.AccessLevel.OWNER, models.AccessLevel.ADMIN]))])
async def delete_project(project_id: int):
    return impl.impl_delete_project(project_id)


@router.post("/{project_id}/participants",
             summary="Add participant to project",
             description="Add a participant to a project",
             dependencies=[Depends(ProjectAccessChecker([models.AccessLevel.OWNER, models.AccessLevel.ADMIN]))])
async def post_participant(project_id: int, user_id: int, access_level: models.AccessLevel):
    return impl.impl_post_participant(project_id, user_id, access_level)


@router.delete("/{project_id}/participants/{user_id}",
               summary="Remove project participant",
               response_model=bool,
               description="Remove a participant from a project",
               dependencies=[Depends(ProjectAccessChecker([models.AccessLevel.OWNER, models.AccessLevel.ADMIN]))])
async def delete_participant(project_id: int, user_id: int):
    return impl.impl_delete_participant(project_id, user_id)


@router.put("/{project_id}/name",
            summary="Set project name",
            description="Update the name of the project",
            dependencies=[Depends(ProjectAccessChecker([models.AccessLevel.OWNER]))],
            response_model=bool)
async def put_participant_name(project_id: int, name: str):
    return impl.impl_put_name(project_id, name)


@router.get("/{project_id}/subprojects",
            summary="Get subprojects in project",
            dependencies=[Depends(ProjectAccessChecker(models.AccessLevel.list_can_read()))],
            response_model=List[models.SubProject])
async def get_subprojects(project_id: int):
    return impl.impl_get_subprojects(project_id)


@router.get("/{project_id}/subprojects/{subproject_id}",
            summary="Get subproject",
            response_model=models.SubProject,
            description="Get a specific project using subproject ID")
async def get_subproject(project_id: int, subproject_id: int):
    return impl.impl_get_subproject(project_id, subproject_id)


@router.post("/{project_id}/subprojects",
             summary="Create subproject",
             description="Create a new subproject. Needs to be connected to an existing project.",
             response_model=models.SubProject,
             dependencies=[Depends(ProjectAccessChecker([models.AccessLevel.OWNER, models.AccessLevel.ADMIN]))])
async def post_subproject(project_id: int, subproject: models.SubProjectPost,
                          current_user: User = Depends(get_current_active_user)):
    return impl.impl_post_subproject(subproject, current_user.id, project_id=project_id)


@router.delete("/{project_id}/subprojects/{subproject_id}",
               summary="Delete project",
               description="Delete a project",
               response_model=bool,
               dependencies=[Depends(ProjectAccessChecker(models.AccessLevel.list_are_admins()))])
async def delete_subproject(project_id: int, subproject_id: int):
    return impl.impl_delete_subproject(project_id, subproject_id)


@router.get("/apps/{app_id}/native-subprojects/{native_project_id}",
            summary="Get application specific native subproject",
            response_model=models.SubProject)
async def get_app_native_project(app_id, native_project_id):
    return impl.impl_get_subproject_native(app_id, native_project_id)


@router.get("/apps/{app_id}/native-subprojects",
            summary="List application specific native subprojects available to the user",
            response_model=List[models.SubProject])
async def get_user_subprojects_with_application_sid(app_id: str, current_user: User = Depends(get_current_active_user),
                                                    no_project_association: Optional[bool] = False):
    return impl.impl_get_user_subprojects_with_application_sid(current_user.id, current_user.id, app_id,
                                                               no_project_association = no_project_association)

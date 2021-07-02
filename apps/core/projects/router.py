from fastapi import APIRouter, Security, Depends

from apps.core.projects.implementation import *
from apps.core.projects.dependencies import ProjectAccessChecker
from apps.core.authentication.utils import verify_token, get_current_active_user
from apps.core.projects.models import ProjectPost, ProjectListing, AccessLevel
from apps.core.users.models import User


router = APIRouter()


@router.get("/",
            summary="Lists all projects",
            description="Lists all projects in alphabetical order",
            response_model=List[ProjectListing])
async def get_projects(segment_length: int, index: int, current_user: User = Depends(get_current_active_user)):
    """
    Lists all projects that the current user has access to
    :param segment_length:
    :param index:
    :return:
    """
    return impl_get_user_projects(current_user.id, segment_length=segment_length, index=index)


@router.get("/all",
            summary="Get all projects",
            description="Lists all projects that exist, and is only available to those who have the authority.",
            dependencies=[Security(verify_token, scopes=['admin'])])
async def get_all_projects(segment_length: int, index: int):
    """
    Lists all projects that exists, and is only available to those who have the authority.
    :param segment_length:
    :param index:
    :return:
    """
    return impl_get_projects(segment_length, index)


@router.get("/{project_id}",
            summary="Get project",
            description="Get a specific project using project ID")
async def get_project(project_id: int):
    return impl_get_project(project_id)


@router.post("/",
             summary="Create project",
             description="Create a new empty project",
             dependencies=[Security(verify_token, scopes=['admin'])])
async def post_project(project: ProjectPost):
    return impl_post_project(project)


@router.delete("/{project_id}",
               summary="Delete project",
               description="Delete a project",
               dependencies=[Security(verify_token, scopes=['admin'])])
async def delete_project(project_id: int):
    return impl_delete_project(project_id)


@router.post("/{project_id}/participants/",
             summary="Add participant to project",
             description="Add a participant to a project",
             dependencies=[Depends(ProjectAccessChecker([AccessLevel.OWNER, AccessLevel.ADMIN]))])
async def post_participant(project_id: int, user_id: int, access_level: AccessLevel):
    return impl_post_participant(project_id, user_id, access_level)


@router.delete("/{project_id}/participants/{user_id}",
               summary="Remove project participant",
               description="Remove a participant from a project",
               dependencies=[Depends(ProjectAccessChecker([AccessLevel.OWNER, AccessLevel.ADMIN]))])
async def delete_participant(project_id: int, user_id: int):
    return impl_delete_participant(project_id, user_id)


@router.put("/{project_id}/name",
            summary="Set project name",
            description="Update the name of the project",
            dependencies=[Depends(ProjectAccessChecker([AccessLevel.OWNER]))],
            response_model=bool)
async def put_participant_name(project_id: int, name: str):
    return impl_put_name(project_id, name)


@router.get("/{project_id}/subproject/{subproject_id}",
            summary="Get subproject",
            description="Get a specific project using subproject ID")
async def get_subproject(project_id: int, subproject_id: int):
    return impl_get_subproject(project_id, subproject_id)


@router.get("/application-native-subproject/",
            summary="Get subproject using application native ID",
            description="Get subproject using application native ID and application string ID")
async def get_subproject_native(application_sid: str, native_project_id: int):
    return impl_get_subproject_native(application_sid, native_project_id)


@router.post("/{project_id}/subproject/",
             summary="Create subproject",
             description="Create a new subproject. Needs to be connected to an existing project.",
             response_model=SubProject,
             dependencies=[Security(verify_token),
                           Depends(ProjectAccessChecker([AccessLevel.OWNER, AccessLevel.ADMIN]))])
async def post_subproject(project_id: int, subproject: SubProjectPost,
                          current_user: User = Depends(get_current_active_user)):
    return impl_post_subproject(subproject, current_user.id, project_id=project_id)


@router.delete("/{project_id}/subproject/{subproject_id}",
               summary="Delete project",
               description="Delete a project",
               dependencies=[Security(verify_token, scopes=['admin'])])
async def delete_subproject(project_id: int, subproject_id: int):
    return impl_delete_subproject(project_id, subproject_id)

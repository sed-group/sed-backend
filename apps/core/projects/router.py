from fastapi import APIRouter, Security

from apps.core.projects.implementation import (impl_get_projects, impl_get_project, impl_post_project,
                                               impl_delete_project, impl_post_participant, impl_delete_participant,
                                               impl_put_name)
from apps.core.authentication.utils import verify_token
from apps.core.projects.models import ProjectPost, ProjectListing, AccessLevel

router = APIRouter()


@router.get("/",
            summary="Lists all projects",
            description="Lists all projects in alphabetical order",
            dependencies=[Security(verify_token)])
async def get_projects(segment_length: int, index: int):
    """

    :param segment_length:
    :param index:
    :return:
    """
    return impl_get_projects(segment_length, index)


@router.get("/{project_id}",
            summary="Get project",
            description="Get a specific project using project ID",
            dependencies=[Security(verify_token)])
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
             dependencies=[Security(verify_token, scopes=['admin'])])
async def post_participant(project_id: int, user_id: int, access_level: AccessLevel):
    return impl_post_participant(project_id, user_id, access_level)


@router.delete("/{project_id}/participants/{user_id}",
               summary="Remove project participant",
               description="Remove a participant from a project",
               dependencies=[Security(verify_token, scopes=['admin'])])
async def post_participant(project_id: int, user_id: int):
    return impl_delete_participant(project_id, user_id)


@router.post("/{project_id}/name",
             summary="Set project name",
             description="Update the name of the project",
             dependencies=[Security(verify_token, scopes=['admin'])])
async def post_participant(project_id: int, name: str):
    return impl_put_name(project_id, name)

from fastapi import APIRouter, Security

from apps.core.projects.implementation import impl_get_projects, impl_get_project, impl_post_project
from apps.core.authentication.utils import verify_token
from apps.core.projects.models import ProjectPost, ProjectListing

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
            summary="",
            dependencies=[Security(verify_token)])
async def get_project(project_id: int):
    return impl_get_project(project_id)


@router.post("/",
             summary="",
             description="",
             dependencies=[Security(verify_token)])
async def post_project(project: ProjectPost):
    return impl_post_project(project)


from fastapi import APIRouter, Security

from apps.core.applications.implementation import impl_get_apps, impl_post_app, impl_get_app, impl_delete_app
from apps.core.authentication.utils import verify_token
from apps.core.applications.models import Application

router = APIRouter()


@router.get("/",
            summary="Lists all applications",
            description="Produces a list of applications in alphabetical order",
            dependencies=[Security(verify_token)])
async def get_apps(segment_length: int, index: int):
    return impl_get_apps(segment_length, index)


@router.post("/",
             summary="Insert new application",
             dependencies=[Security(verify_token, scopes=['admin'])])
async def post_app(app: Application):
    return impl_post_app(app)


@router.get("/{app_id}",
            summary="Lists all applications",
            description="Produces a list of applications in alphabetical order",
            dependencies=[Security(verify_token)])
async def get_app(app_id: int):
    return impl_get_app(app_id)


@router.delete("/{app_id}",
               summary="Remove an application",
               dependencies=[Security(verify_token, scopes=['admin'])])
async def delete_app(app_id: int):
    return impl_delete_app(app_id)

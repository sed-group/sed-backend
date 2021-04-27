from fastapi import APIRouter

from apps.core.users.router import router as router_users
from apps.core.authentication.router import router as router_auth
from apps.core.applications.router import router as router_apps
from apps.core.projects.router import router as router_projects

router = APIRouter()

router.include_router(router_users, prefix='/users', tags=['users'])
router.include_router(router_auth, prefix='/auth', tags=['authentication'])
router.include_router(router_apps, prefix='/apps', tags=['applications'])
router.include_router(router_projects, prefix='/projects', tags=['projects'])


@router.get("/", summary="Core API root", description="This is pointless", tags=['core'])
async def get_api_root():
    return {"version": "2"}

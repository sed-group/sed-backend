from fastapi import APIRouter, Security

from apps.core.users.router import router as router_users
from apps.core.authentication.router import router as router_auth
from apps.core.authentication.utils import verify_token
from apps.core.applications.router import router as router_apps
from apps.core.projects.router import router as router_projects
from apps.core.individuals.router import router as router_individuals
from apps.core.measurements.router import router as router_measurements

router = APIRouter()

router.include_router(router_auth, prefix='/auth', tags=['authentication'])
router.include_router(router_users, prefix='/users', tags=['users'], dependencies=[Security(verify_token)])
router.include_router(router_apps, prefix='/apps', tags=['applications'], dependencies=[Security(verify_token)])
router.include_router(router_projects, prefix='/projects', tags=['projects'], dependencies=[Security(verify_token)])
router.include_router(router_individuals, prefix='/individuals', tags=['individuals'], dependencies=[Security(verify_token)])
router.include_router(router_measurements, prefix='/data', tags=['data'])


@router.get("/", summary="Core API root", description="This is pointless", tags=['core'])
async def get_api_root():
    return {"version": "2"}

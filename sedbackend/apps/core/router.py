from datetime import datetime

from fastapi import APIRouter, Security

from sedbackend.apps.core.implementation import impl_check_db_connection

from sedbackend.apps.core.users.router import router as router_users
from sedbackend.apps.core.authentication.router import router as router_auth
from sedbackend.apps.core.authentication.utils import verify_token
from sedbackend.apps.core.applications.router import router as router_apps
from sedbackend.apps.core.projects.router import router as router_projects
from sedbackend.apps.core.individuals.router import router as router_individuals
from sedbackend.apps.core.measurements.router import router as router_measurements
from sedbackend.apps.core.files.router import router as router_files

router = APIRouter()

router.include_router(router_auth, prefix='/auth', tags=['authentication'])
router.include_router(router_users, prefix='/users', tags=['users'], dependencies=[Security(verify_token)])
router.include_router(router_apps, prefix='/apps', tags=['applications'], dependencies=[Security(verify_token)])
router.include_router(router_projects, prefix='/projects', tags=['projects'], dependencies=[Security(verify_token)])
router.include_router(router_individuals, prefix='/individuals', tags=['individuals'], dependencies=[Security(verify_token)])
router.include_router(router_measurements, prefix='/data', tags=['data'], dependencies=[Security(verify_token)])
router.include_router(router_files, prefix='/files', tags=['files'], dependencies=[Security(verify_token)])

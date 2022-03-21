from fastapi import APIRouter, Security

from sedbackend.apps.core.authentication.utils import verify_token
from sedbackend.apps.core.router import router as core_router
from sedbackend.apps.difam.router import router as difam_router
from sedbackend.apps.cvs.router import router as cvs_router

# main api router
router = APIRouter()

# sub-routers
router.include_router(core_router, prefix='/core')
router.include_router(difam_router, prefix='/difam', tags=['difam'], dependencies=[Security(verify_token)])
router.include_router(cvs_router, prefix='/cvs', tags=['cvs'], dependencies=[Security(verify_token)])

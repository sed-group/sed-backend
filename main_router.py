from fastapi import APIRouter, Security

from apps.core.authentication.utils import verify_token
from apps.core.router import router as core_router
from apps.EFMbackend.router import router as efm_router
from apps.difam.router import router as difam_router

# main api router
router = APIRouter()

# sub-routers
# router.include_router(core_router, prefix='/core')  # Core module has no prefix
router.include_router(efm_router, prefix="/efm", tags=['EF-M'], dependencies=[Security(verify_token)])
router.include_router(core_router, prefix='/core')
router.include_router(difam_router, prefix='/difam', tags=['difam'], dependencies=[Security(verify_token)])

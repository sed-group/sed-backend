from fastapi import APIRouter

from apps.core.router import router as core_router
from apps.EFMbackend.router import router as efm_router

# main api router
router = APIRouter()

# sub-routers
router.include_router(core_router, prefix='/core')  # Core module has no prefix
router.include_router(efm_router, prefix="/efm", tags=['EF-M'])
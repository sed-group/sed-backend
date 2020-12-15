from fastapi import APIRouter, Depends, HTTPException

from apps.core.router import router as core_router

# main api router
router = APIRouter()

# sub-routers
router.include_router(core_router)  # Core module has no prefix

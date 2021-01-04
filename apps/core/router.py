from fastapi import APIRouter, Depends, HTTPException

from apps.core.routes.users import router as router_users
from apps.core.routes.auth import router as router_auth

router = APIRouter()

router.include_router(router_users, prefix='/users')
router.include_router(router_auth, prefix='/auth')


@router.get("/")
async def get_api_root():
    return {"version": "1"}

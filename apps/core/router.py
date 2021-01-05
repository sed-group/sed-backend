from fastapi import APIRouter

from apps.core.users.router import router as router_users
from apps.core.authentication.router import router as router_auth

router = APIRouter()

router.include_router(router_users, prefix='/users', tags=['core', 'users'])
router.include_router(router_auth, prefix='/auth', tags=['core', 'authentication'])


@router.get("/", summary="Core API root", description="This is pointless", tags=['core'])
async def get_api_root():
    return {"version": "1"}

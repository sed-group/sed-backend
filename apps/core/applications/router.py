from fastapi import APIRouter, Security

from apps.core.authentication.utils import verify_token


router = APIRouter()


@router.get("/list",
            summary="Lists all users",
            description="Produces a list of users in alphabetical order",
            dependencies=[Security(verify_token)])
async def get_users(segment_length: int, index: int):
    return [
        {

        },
    ]
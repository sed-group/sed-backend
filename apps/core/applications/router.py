from typing import List

from fastapi import APIRouter, Security

from apps.core.applications.implementation import impl_get_apps, impl_get_app
from apps.core.authentication.utils import verify_token
from apps.core.applications.models import Application

router = APIRouter()


@router.get("",
            summary="Lists all applications",
            description="Produces a list of applications in alphabetical order",
            response_model=List[Application],
            dependencies=[Security(verify_token)])
async def get_apps() -> List[Application]:
    """

    :param segment_length: Sample size. Min=1.
    :param index: Offset, multiplied by segment_length. Min=0 (no offset).
    :return:
    """
    return impl_get_apps()


@router.get("/{app_id}",
            summary="Get application by ID",
            description="Produces a list of applications in alphabetical order",
            response_model=Application,
            dependencies=[Security(verify_token)])
async def get_app(app_id: str) -> Application:
    return impl_get_app(app_id)

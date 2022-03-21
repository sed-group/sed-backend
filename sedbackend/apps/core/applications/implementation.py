from typing import List

from fastapi import HTTPException

from sedbackend.apps.core.applications.exceptions import ApplicationNotFoundException
from sedbackend.apps.core.applications.state import get_application_list, get_application
from sedbackend.apps.core.applications.models import Application


def impl_get_apps() -> List[Application]:
    return get_application_list()


def impl_get_app(app_id: str) -> Application:
    try:
        return get_application(app_id)
    except ApplicationNotFoundException:
        raise HTTPException(
            status_code=400,
            detail=f"No application found with id = {app_id}"
        )

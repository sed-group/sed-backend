from typing import List, Optional

from fastapi import HTTPException, Request, status
from fastapi.logger import logger

from apps.core.projects.models import AccessLevel
from apps.core.projects.implementation import impl_get_project, impl_get_subproject_native


class ProjectAccessChecker:
    def __init__(self, allowed_levels: List[AccessLevel]):
        self.access_levels = allowed_levels

    def __call__(self, project_id: int, request: Request):
        logger.debug(f'Does user with id {request.state.user_id} have the appropriate access levels?')
        user_id = request.state.user_id

        project = impl_get_project(project_id)
        access = project.participants_access[user_id]
        if access in self.access_levels:
            logger.debug(f"Yes, user {user_id} has access level {access}")
            return True

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User does not have the necessary access level",
        )


class SubProjectAccessChecker:
    def __init__(self, allowed_levels: List[AccessLevel], application_sid: str):
        self.access_levels = allowed_levels
        self.application_sid = application_sid

    def __call__(self, native_project_id: int, request: Request):
        logger.debug(f'Does user with id {request.state.user_id} '
                     f'have access of type {self.access_levels} '
                     f'to sub project with native id = {native_project_id}, '
                     f'in application with sid {self.application_sid}?')

        user_id = request.state.user_id
        # Get subproject
        subproject = impl_get_subproject_native(self.application_sid, native_project_id)
        # Get project
        project = impl_get_project(subproject.project_id)
        # Check user access level in that project
        access = project.participants_access[user_id]
        if access in self.access_levels:
            logger.debug(f"Yes, user {user_id} has access level {access}")
            return True

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User does not have the necessary access level",
        )

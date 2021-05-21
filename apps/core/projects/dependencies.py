from typing import List, Optional

from fastapi import HTTPException, Request, status
from fastapi.logger import logger

from apps.core.projects.models import AccessLevel
from apps.core.projects.implementation import impl_get_project, impl_get_sub_project


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
            detail="You don't have the necessary access level",
        )


class SubProjectAccessChecker:
    def __init__(self, allowed_levels: List[AccessLevel]):
        self.access_levels = allowed_levels

    def __call__(self, sub_project_id: int, request: Request):
        logger.debug(f'Does user with id {request.state.user_id} have access of type {self.access_levels} '
                     f'to sub project with id = {sub_project_id}?')
        user_id = request.state.user_id

        project = impl_get_sub_project(sub_project_id)

        # TODO: Use sub project to fetch the project. Then, chech was access-level the user has to the project.

from typing import List

from fastapi import Request
from fastapi.logger import logger

from sedbackend.apps.core.projects.dependencies import SubProjectAccessChecker
from sedbackend.apps.core.projects.models import AccessLevel
from sedbackend.apps.core.projects.implementation import impl_get_subproject_by_id
from sedbackend.apps.core.files.implementation import impl_get_file_mapped_subproject_id


class FileAccessChecker:
    def __init__(self, allowed_levels: List[AccessLevel]):
        self.access_levels = allowed_levels

    def __call__(self, file_id: int, request: Request):
        logger.debug(f'Is user with id {request.state.user_id} '
                     f'allowed to access file with id {file_id}?')
        user_id = request.state.user_id

        # Get subproject ID
        subproject_id = impl_get_file_mapped_subproject_id(file_id)

        # Run subproject access check
        subproject = impl_get_subproject_by_id(subproject_id)
        return SubProjectAccessChecker.check_user_subproject_access(subproject, self.access_levels, user_id)

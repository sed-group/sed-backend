from fastapi import HTTPException, status

from libs.datastructures.pagination import ListChunk

import apps.core.individuals.exceptions as ind_ex
import apps.core.authentication.exceptions as auth_ex
from apps.core.db import get_connection

import apps.cvs.exceptions as exceptions
import apps.cvs.models as models
import apps.cvs.storage as storage


def get_cvs_projects(segment_length: int, index: int, current_user_id: int) -> ListChunk[models.CVSProject]:
    with get_connection() as con:
        return storage.get_cvs_projects(con, segment_length, index, current_user_id)


def get_cvs_project(project_id: int) -> models.CVSProject:
    try:
        with get_connection() as con:
            return storage.get_cvs_project(con, project_id)
    except exceptions.CVSProjectNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'No CVS project with id = {project_id} could be found.',
        )


def create_cvs_project(project_post: models.CVSProjectPost, user_id: int) -> models.CVSProject:
    try:
        with get_connection() as db_connection:
            result = storage.create_cvs_project(db_connection, project_post, user_id)
            db_connection.commit()
            return result
    except ind_ex.IndividualNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'No user with id = {user_id} found.',
        )


def delete_cvs_project(project_id: int, user_id: int) -> bool:
    try:
        with get_connection() as con:
            res = storage.delete_cvs_project(con, project_id, user_id)
            con.commit()
            return res
    except exceptions.CVSProjectNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='No such project.',
        )
    except exceptions.CVSProjectFailedDeletionException:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='Failed to remove the project.',
        )
    except auth_ex.UnauthorizedOperationException:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Unauthorized unfortunately.',
        )

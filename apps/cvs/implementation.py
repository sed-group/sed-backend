from fastapi import HTTPException, status

from libs.datastructures.pagination import ListChunk

import apps.core.individuals.exceptions as ind_ex
import apps.core.authentication.exceptions as auth_ex
from apps.core.db import get_connection

import apps.cvs.exceptions as cvs_exceptions
import apps.cvs.models as models
import apps.cvs.storage as storage


def get_cvs_projects(segment_length: int, index: int, user_id: int) -> ListChunk[models.CVSProject]:
    with get_connection() as con:
        return storage.get_cvs_projects(con, segment_length, index, user_id)


def get_cvs_project(project_id: int, current_user_id: int) -> models.CVSProject:
    try:
        with get_connection() as con:
            return storage.get_cvs_project(con, project_id, current_user_id)
    except cvs_exceptions.CVSProjectNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'No CVS project with id = {project_id} could be found.',
        )
    except auth_ex.UnauthorizedOperationException:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Unauthorized unfortunately.',
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


def edit_cvs_project(project_id: int, user_id: int, project_post: models.CVSProjectPost) -> models.CVSProject:
    try:
        with get_connection() as db_connection:
            result = storage.edit_cvs_project(db_connection, project_id, user_id, project_post)
            db_connection.commit()
            return result
    except cvs_exceptions.CVSProjectNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='No such project.',
        )
    except cvs_exceptions.CVSProjectFailedToUpdateException:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='Failed to edit the project.',
        )
    except auth_ex.UnauthorizedOperationException:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Unauthorized unfortunately.',
        )


def delete_cvs_project(project_id: int, user_id: int) -> bool:
    try:
        with get_connection() as con:
            res = storage.delete_cvs_project(con, project_id, user_id)
            con.commit()
            return res
    except cvs_exceptions.CVSProjectNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='No such project.',
        )
    except cvs_exceptions.CVSProjectFailedDeletionException:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='Failed to remove the project.',
        )
    except auth_ex.UnauthorizedOperationException:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Unauthorized unfortunately.',
        )

from fastapi import HTTPException
from starlette import status


from sedbackend.apps.core.authentication import exceptions as auth_ex
from sedbackend.apps.core.db import get_connection
from sedbackend.apps.cvs.project import models, exceptions, storage
from sedbackend.libs.datastructures.pagination import ListChunk


def get_all_cvs_project(user_id: int) -> ListChunk[models.CVSProject]:
    with get_connection() as con:
        return storage.get_all_cvs_project(con, user_id)


def get_cvs_project(project_id: int) -> models.CVSProject:
    try:
        with get_connection() as con:
            return storage.get_cvs_project(con, project_id)
    except exceptions.CVSProjectNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Could not find project with id={project_id}.',
        )
    except auth_ex.UnauthorizedOperationException:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Unauthorized user.',
        )


def create_cvs_project(project_post: models.CVSProjectPost, user_id: int) -> models.CVSProject:
    with get_connection() as con:
        result = storage.create_cvs_project(con, project_post, user_id)
        con.commit()
        return result


def edit_cvs_project(project_id: int, project_post: models.CVSProjectPost) -> models.CVSProject:
    try:
        with get_connection() as con:
            result = storage.edit_cvs_project(con, project_id, project_post)
            con.commit()
            return result
    except exceptions.CVSProjectNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Could not find project with id={project_id}.',
        )
    except exceptions.CVSProjectFailedToUpdateException:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'Failed to edit project with id={project_id}.',
        )
    except auth_ex.UnauthorizedOperationException:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Unauthorized user.',
        )


def delete_cvs_project(project_id: int, user_id: int) -> bool:
    try:
        with get_connection() as con:
            res = storage.delete_cvs_project(con, project_id, user_id)
            con.commit()
            return res
    except exceptions.CVSProjectFailedDeletionException:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'Failed to remove project with id={project_id}.',
        )
    except auth_ex.UnauthorizedOperationException:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Unauthorized user.',
        )

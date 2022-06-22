from typing import List

from fastapi import HTTPException
from starlette import status

from sedbackend.apps.core.authentication import exceptions as auth_ex
from sedbackend.apps.core.db import get_connection
import sedbackend.apps.cvs.project.exceptions as project_exceptions
from sedbackend.apps.cvs.vcs import models, storage, exceptions
from sedbackend.libs.datastructures.pagination import ListChunk


# ======================================================================================================================
# VCS
# ======================================================================================================================

def get_all_vcs(project_id: int, user_id: int) -> ListChunk[models.VCS]:
    with get_connection() as con:
        return storage.get_all_vcs(con, project_id, user_id)


def get_segment_vcs(project_id: int, index: int, segment_length: int, user_id: int) -> ListChunk[models.VCS]:
    try:
        with get_connection() as con:
            return storage.get_segment_vcs(con, project_id, segment_length, index, user_id)
    except project_exceptions.CVSProjectNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Could not find project with id={project_id}.',
        )
    except auth_ex.UnauthorizedOperationException:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Unauthorized user.',
        )


def get_vcs(vcs_id: int, project_id: int, user_id: int) -> models.VCS:
    try:
        with get_connection() as con:
            return storage.get_vcs(con, vcs_id, project_id, user_id)
    except project_exceptions.CVSProjectNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Could not find project with id={project_id}.',
        )
    except exceptions.VCSNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Could not find VCS with id={vcs_id}.',
        )
    except auth_ex.UnauthorizedOperationException:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Unauthorized user.',
        )


def create_vcs(vcs_post: models.VCSPost, project_id: int, user_id: int) -> models.VCS:
    try:
        with get_connection() as con:
            result = storage.create_vcs(con, vcs_post, project_id, user_id)
            con.commit()
            return result
    except project_exceptions.CVSProjectNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Could not find project with id={project_id}.',
        )
    except auth_ex.UnauthorizedOperationException:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Unauthorized user.',
        )


def edit_vcs(vcs_id: int, project_id: int, user_id: int, vcs_post: models.VCSPost) -> models.VCS:
    try:
        with get_connection() as con:
            result = storage.edit_vcs(con, vcs_id, project_id, user_id, vcs_post)
            con.commit()
            return result
    except project_exceptions.CVSProjectNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Could not find project with id={project_id}.',
        )
    except exceptions.VCSNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Could not find VCS with id={vcs_id}.',
        )
    except exceptions.VCSFailedToUpdateException:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'Failed to edit VCS with id={vcs_id}.',
        )
    except auth_ex.UnauthorizedOperationException:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Unauthorized user.',
        )


def delete_vcs(vcs_id: int, project_id: int, user_id: int) -> bool:
    try:
        with get_connection() as con:
            res = storage.delete_vcs(con, vcs_id, project_id, user_id)
            con.commit()
            return res
    except project_exceptions.CVSProjectNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Could not find project with id={project_id}.',
        )
    except exceptions.VCSNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Could not find VCS with id={vcs_id}.',
        )
    except exceptions.VCSFailedDeletionException:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'Failed to remove VCS with id={vcs_id}.',
        )
    except auth_ex.UnauthorizedOperationException:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Unauthorized user.',
        )


# ======================================================================================================================
# VCS Value driver
# ======================================================================================================================


def get_all_value_driver(vcs_id: int) -> List[models.ValueDriver]:
    try:
        with get_connection() as con:
            return storage.get_all_value_driver(con, vcs_id)
    except exceptions.VCSNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Could not find vcs with id={vcs_id}.',
        )
    except exceptions.ValueDriverNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Could not find value drivers in vcs with id={vcs_id}'
        )


def get_value_driver(value_driver_id: int) -> models.ValueDriver:
    try:
        with get_connection() as con:
            return storage.get_value_driver(con, value_driver_id)
    except exceptions.ValueDriverNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Could not find value driver with id={value_driver_id}.',
        )
    except auth_ex.UnauthorizedOperationException:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Unauthorized user.',
        )


def create_value_driver(vcs_id: int, value_driver_post: models.ValueDriverPost) -> models.ValueDriver:
    try:
        with get_connection() as con:
            result = storage.create_value_driver(con, vcs_id, value_driver_post)
            con.commit()
            return result
    except auth_ex.UnauthorizedOperationException:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Unauthorized user.',
        )


def edit_value_driver(value_driver_id: int,
                      value_driver_post: models.ValueDriverPost) -> models.ValueDriver:
    try:
        with get_connection() as con:
            result = storage.edit_value_driver(con, value_driver_id, value_driver_post)
            con.commit()
            return result
    except exceptions.ValueDriverNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Could not find value driver with id={value_driver_id}.',
        )
    except exceptions.ValueDriverFailedToUpdateException:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'Failed to edit value driver with id={value_driver_id}.',
        )
    except auth_ex.UnauthorizedOperationException:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Unauthorized user.',
        )


def delete_value_driver(value_driver_id: int) -> bool:
    try:
        with get_connection() as con:
            res = storage.delete_value_driver(con, value_driver_id)
            con.commit()
            return res
    except exceptions.ValueDriverNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Could not find value driver with id={value_driver_id}.',
        )
    except exceptions.ValueDriverFailedDeletionException:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'Failed to remove value driver with id={value_driver_id}.',
        )
    except auth_ex.UnauthorizedOperationException:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Unauthorized user.',
        )


# ======================================================================================================================
# VCS ISO Processes
# ======================================================================================================================


def get_all_iso_process() -> List[models.VCSISOProcess]:
    try:
        with get_connection() as con:
            res = storage.get_all_iso_process(con)
            con.commit()
            return res
    except exceptions.ISOProcessNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Could not find any ISO processes'
        )


def get_iso_process(iso_process_id: int) -> models.VCSISOProcess:
    try:
        with get_connection() as con:
            res = storage.get_iso_process(iso_process_id, con)
            con.commit()
            return res
    except exceptions.ISOProcessNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Could not find ISO process with id={iso_process_id}.',
        )

# ======================================================================================================================
# VCS Subprocesses
# ======================================================================================================================


def get_all_subprocess(vcs_id: int, user_id: int) -> List[models.VCSSubprocess]:
    with get_connection() as con:
        return storage.get_all_subprocess(con, vcs_id, user_id)


def get_subprocess(subprocess_id: int) -> models.VCSSubprocess:
    try:
        with get_connection() as con:
            return storage.get_subprocess(con, subprocess_id)
    except project_exceptions.CVSProjectNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Could not find project.',
        )
    except exceptions.SubprocessNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Could not find subprocess with id={e.subprocess_id}.',
        )
    except auth_ex.UnauthorizedOperationException:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Unauthorized user.',
        )


def create_subprocess(subprocess_post: models.VCSSubprocessPost) -> models.VCSSubprocess:
    try:
        with get_connection() as con:
            result = storage.create_subprocess(con, subprocess_post)
            con.commit()
            return result
    except project_exceptions.CVSProjectNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Could not find project.',
        )
    except exceptions.ISOProcessNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Could not find ISO process with id={subprocess_post.parent_process_id}.',
        )
    except auth_ex.UnauthorizedOperationException:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Unauthorized user.',
        )
    except exceptions.GenericDatabaseException as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=err.msg
        )


def edit_subprocess(subprocess_id: int, project_id: int, user_id: int,
                    subprocess_post: models.VCSSubprocessPost) -> models.VCSSubprocess:
    try:
        with get_connection() as con:
            result = storage.edit_subprocess(con, subprocess_id, project_id, user_id, subprocess_post)
            con.commit()
            return result
    except project_exceptions.CVSProjectNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Could not find project with id={project_id}.',
        )
    except exceptions.SubprocessNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Could not find subprocess with id={e.subprocess_id}.',
        )
    except exceptions.ISOProcessNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Could not find ISO process with id={subprocess_post.parent_process_id}.',
        )
    except exceptions.SubprocessFailedToUpdateException as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'Failed to edit subprocess with id={e.subprocess_id}.',
        )
    except auth_ex.UnauthorizedOperationException:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Unauthorized user.',
        )


def delete_subprocess(subprocess_id: int) -> bool:
    try:
        with get_connection() as con:
            res = storage.delete_subprocess(con, subprocess_id)
            con.commit()
            return res
    except project_exceptions.CVSProjectNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Could not find project.',
        )
    except exceptions.SubprocessNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Could not find subprocess with id={e.subprocess_id}.',
        )
    except exceptions.SubprocessFailedDeletionException as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'Failed to remove subprocess with id={e.subprocess_id}.',
        )
    except auth_ex.UnauthorizedOperationException:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Unauthorized user.',
        )


def update_indices_subprocess(subprocess_ids: List[int], order_indices: List[int], project_id: int,
                              user_id: int) -> bool:
    try:
        with get_connection() as con:
            result = storage.update_subprocess_indices(con, subprocess_ids, order_indices, project_id, user_id)
            con.commit()
            return result
    except project_exceptions.CVSProjectNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Could not find project with id={project_id}.',
        )
    except exceptions.SubprocessNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Could not find subprocess with id={e.subprocess_id}.',
        )
    except exceptions.SubprocessFailedToUpdateException as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'Failed to edit subprocess with id={e.subprocess_id}.',
        )
    except auth_ex.UnauthorizedOperationException:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Unauthorized user.',
        )


# ======================================================================================================================
# VCS Table
# ======================================================================================================================


def get_vcs_table(vcs_id: int, user_id: int) -> List[models.VcsRow]:
    try:
        with get_connection() as con:
            return storage.get_vcs_table(con, vcs_id,  user_id)
    except auth_ex.UnauthorizedOperationException:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Unauthorized user.',
        )


def create_vcs_table(new_table: List[models.VcsRowPost], vcs_id: int)-> bool:
    try:
        with get_connection() as con:
            result = storage.create_vcs_table(con, new_table, vcs_id)
            con.commit()
            return result
    except exceptions.VCSTableRowFailedDeletionException as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'Failed to remove VCS table row with id={e.table_row_id}.',
        )
    except exceptions.VCSTableProcessAmbiguity as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Both ISO process and subprocess was provided for table row with index={e.table_row_id}.',
        )
    except exceptions.ValueDriverNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Could not find value driver with id={e.value_driver_id}.',
        )
    except exceptions.ISOProcessNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='No such ISO process'
        )
    except exceptions.SubprocessNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='No such subprocess'
        )
    except auth_ex.UnauthorizedOperationException:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Unauthorized user.',
        )

def edit_vcs_table(updated_vcs_rows: List[models.VcsRow], vcs_id: int) -> bool:
    try: 
        with get_connection() as con:
            res = storage.edit_vcs_table(con, updated_vcs_rows, vcs_id)
            con.commit()
            return res
    except exceptions.VCSTableRowFailedToUpdateException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Could not update vcs table'
        )
    except exceptions.VCSTableProcessAmbiguity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Ambiguity in iso processes and subprocesses'
        )
    except exceptions.ValueDriverFailedDeletionException:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'Could not delete value driver'
        )
    except exceptions.ValueDimensionFailedDeletionException:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'Could not delete value dimension'
        )

def delete_vcs_row(vcs_row_id: int, vcs_id: int) -> bool:
    try:
        with get_connection() as con:
            res = storage.delete_vcs_row(con, vcs_row_id, vcs_id)
            con.commit()
            return res
    except exceptions.VCSTableRowFailedDeletionException:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'Could not delete vcs row'
        )


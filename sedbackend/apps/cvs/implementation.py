from fastapi import HTTPException, status
from typing import List

from sedbackend.libs.datastructures.pagination import ListChunk

import sedbackend.apps.core.authentication.exceptions as auth_ex
from sedbackend.apps.core.db import get_connection
import sedbackend.apps.cvs.models as models
import sedbackend.apps.cvs.storage as storage
import sedbackend.apps.cvs.exceptions as cvs_exceptions


# ======================================================================================================================
# CVS projects
# ======================================================================================================================

def get_all_cvs_project(user_id: int) -> ListChunk[models.CVSProject]:
    with get_connection() as con:
        return storage.get_all_cvs_project(con, user_id)


def get_segment_cvs_project(index: int, segment_length: int, user_id: int) -> ListChunk[models.CVSProject]:
    with get_connection() as con:
        return storage.get_segment_cvs_project(con, index, segment_length, user_id)


def get_cvs_project(project_id: int, user_id: int) -> models.CVSProject:
    try:
        with get_connection() as con:
            return storage.get_cvs_project(con, project_id, user_id)
    except cvs_exceptions.CVSProjectNotFoundException:
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


def edit_cvs_project(project_id: int, user_id: int, project_post: models.CVSProjectPost) -> models.CVSProject:
    try:
        with get_connection() as con:
            result = storage.edit_cvs_project(con, project_id, user_id, project_post)
            con.commit()
            return result
    except cvs_exceptions.CVSProjectNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Could not find project with id={project_id}.',
        )
    except cvs_exceptions.CVSProjectFailedToUpdateException:
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
    except cvs_exceptions.CVSProjectNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Could not find project with id={project_id}.',
        )
    except cvs_exceptions.CVSProjectFailedDeletionException:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'Failed to remove project with id={project_id}.',
        )
    except auth_ex.UnauthorizedOperationException:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Unauthorized user.',
        )


# ======================================================================================================================
# VCS (Value Creation Strategy)
# ======================================================================================================================

def get_all_vcs(project_id: int, user_id: int) -> ListChunk[models.VCS]:
    with get_connection() as con:
        return storage.get_all_vcs(con, project_id, user_id)


def get_segment_vcs(project_id: int, index: int, segment_length: int, user_id: int) -> ListChunk[models.VCS]:
    try:
        with get_connection() as con:
            return storage.get_segment_vcs(con, project_id, segment_length, index, user_id)
    except cvs_exceptions.CVSProjectNotFoundException:
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
    except cvs_exceptions.CVSProjectNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Could not find project with id={project_id}.',
        )
    except cvs_exceptions.VCSNotFoundException:
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
    except cvs_exceptions.CVSProjectNotFoundException:
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
    except cvs_exceptions.CVSProjectNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Could not find project with id={project_id}.',
        )
    except cvs_exceptions.VCSNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Could not find VCS with id={vcs_id}.',
        )
    except cvs_exceptions.VCSFailedToUpdateException:
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
    except cvs_exceptions.CVSProjectNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Could not find project with id={project_id}.',
        )
    except cvs_exceptions.VCSNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Could not find VCS with id={vcs_id}.',
        )
    except cvs_exceptions.VCSFailedDeletionException:
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

def get_all_value_driver(project_id: int, user_id: int) -> ListChunk[models.VCSValueDriver]:
    with get_connection() as con:
        return storage.get_all_value_driver(con, project_id, user_id)


def get_value_driver(value_driver_id: int, project_id: int, user_id: int) -> models.VCSValueDriver:
    try:
        with get_connection() as con:
            return storage.get_value_driver(con, value_driver_id, project_id, user_id)
    except cvs_exceptions.CVSProjectNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Could not find project with id={project_id}.',
        )
    except cvs_exceptions.ValueDriverNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Could not find value driver with id={value_driver_id}.',
        )
    except auth_ex.UnauthorizedOperationException:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Unauthorized user.',
        )


def create_value_driver(value_driver_post: models.VCSValueDriverPost, project_id: int,
                        user_id: int) -> models.VCSValueDriver:
    try:
        with get_connection() as con:
            result = storage.create_value_driver(con, value_driver_post, project_id, user_id)
            con.commit()
            return result
    except cvs_exceptions.CVSProjectNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Could not find project with id={project_id}.',
        )
    except auth_ex.UnauthorizedOperationException:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Unauthorized user.',
        )


def edit_value_driver(value_driver_id: int, project_id: int, user_id: int,
                      value_driver_post: models.VCSValueDriverPost) -> models.VCSValueDriver:
    try:
        with get_connection() as con:
            result = storage.edit_value_driver(con, value_driver_id, project_id, user_id, value_driver_post)
            con.commit()
            return result
    except cvs_exceptions.CVSProjectNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Could not find project with id={project_id}.',
        )
    except cvs_exceptions.ValueDriverNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Could not find value driver with id={value_driver_id}.',
        )
    except cvs_exceptions.ValueDriverFailedToUpdateException:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'Failed to edit value driver with id={value_driver_id}.',
        )
    except auth_ex.UnauthorizedOperationException:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Unauthorized user.',
        )


def delete_value_driver(value_driver_id: int, project_id: int, user_id: int) -> bool:
    try:
        with get_connection() as con:
            res = storage.delete_value_driver(con, value_driver_id, project_id, user_id)
            con.commit()
            return res
    except cvs_exceptions.CVSProjectNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Could not find project with id={project_id}.',
        )
    except cvs_exceptions.ValueDriverNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Could not find value driver with id={value_driver_id}.',
        )
    except cvs_exceptions.ValueDriverFailedDeletionException:
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

def get_all_iso_process() -> ListChunk[models.VCSISOProcess]:
    return storage.get_all_iso_process()


def get_iso_process(iso_process_id: int) -> models.VCSISOProcess:
    try:
        return storage.get_iso_process(iso_process_id)
    except cvs_exceptions.ISOProcessNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Could not find ISO process with id={iso_process_id}.',
        )


# ======================================================================================================================
# VCS Subprocesses
# ======================================================================================================================

def get_all_subprocess(project_id: int, user_id: int) -> ListChunk[models.VCSSubprocess]:
    with get_connection() as con:
        return storage.get_all_subprocess(con, project_id, user_id)


def get_subprocess(subprocess_id: int, project_id: int, user_id: int) -> models.VCSSubprocess:
    try:
        with get_connection() as con:
            return storage.get_subprocess(con, subprocess_id, project_id, user_id)
    except cvs_exceptions.CVSProjectNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Could not find project with id={project_id}.',
        )
    except cvs_exceptions.SubprocessNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Could not find subprocess with id={e.subprocess_id}.',
        )
    except auth_ex.UnauthorizedOperationException:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Unauthorized user.',
        )


def create_subprocess(subprocess_post: models.VCSSubprocessPost, project_id: int,
                      user_id: int) -> models.VCSSubprocess:
    try:
        with get_connection() as con:
            result = storage.create_subprocess(con, subprocess_post, project_id, user_id)
            con.commit()
            return result
    except cvs_exceptions.CVSProjectNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Could not find project with id={project_id}.',
        )
    except cvs_exceptions.ISOProcessNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Could not find ISO process with id={subprocess_post.parent_process_id}.',
        )
    except auth_ex.UnauthorizedOperationException:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Unauthorized user.',
        )


def edit_subprocess(subprocess_id: int, project_id: int, user_id: int,
                    subprocess_post: models.VCSSubprocessPost) -> models.VCSSubprocess:
    try:
        with get_connection() as con:
            result = storage.edit_subprocess(con, subprocess_id, project_id, user_id, subprocess_post)
            con.commit()
            return result
    except cvs_exceptions.CVSProjectNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Could not find project with id={project_id}.',
        )
    except cvs_exceptions.SubprocessNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Could not find subprocess with id={e.subprocess_id}.',
        )
    except cvs_exceptions.ISOProcessNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Could not find ISO process with id={subprocess_post.parent_process_id}.',
        )
    except cvs_exceptions.SubprocessFailedToUpdateException as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'Failed to edit subprocess with id={e.subprocess_id}.',
        )
    except auth_ex.UnauthorizedOperationException:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Unauthorized user.',
        )


def delete_subprocess(subprocess_id: int, project_id: int, user_id: int) -> bool:
    try:
        with get_connection() as con:
            res = storage.delete_subprocess(con, subprocess_id, project_id, user_id)
            con.commit()
            return res
    except cvs_exceptions.CVSProjectNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Could not find project with id={project_id}.',
        )
    except cvs_exceptions.SubprocessNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Could not find subprocess with id={e.subprocess_id}.',
        )
    except cvs_exceptions.SubprocessFailedDeletionException as e:
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
    except cvs_exceptions.CVSProjectNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Could not find project with id={project_id}.',
        )
    except cvs_exceptions.SubprocessNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Could not find subprocess with id={e.subprocess_id}.',
        )
    except cvs_exceptions.SubprocessFailedToUpdateException as e:
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

def get_vcs_table(vcs_id: int, project_id: int, user_id: int) -> models.TableGet:
    try:
        with get_connection() as con:
            return storage.get_vcs_table(con, vcs_id, project_id, user_id)
    except auth_ex.UnauthorizedOperationException:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Unauthorized user.',
        )


def create_vcs_table(new_table: models.TablePost, vcs_id: int, project_id: int, user_id: int) -> bool:
    try:
        with get_connection() as con:
            result = storage.create_vcs_table(con, new_table, vcs_id, project_id, user_id)
            con.commit()
            return result
    except cvs_exceptions.VCSTableRowFailedDeletionException as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'Failed to remove VCS table row with id={e.table_row_id}.',
        )
    except cvs_exceptions.VCSTableProcessAmbiguity as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Both ISO process and subprocess was provided for table row with index={e.table_row_id}.',
        )
    except cvs_exceptions.ValueDriverNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Could not find value driver with id={e.value_driver_id}.',
        )
    except auth_ex.UnauthorizedOperationException:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Unauthorized user.',
        )

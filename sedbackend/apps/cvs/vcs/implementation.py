from typing import List, Tuple

from fastapi import HTTPException
from starlette import status

from sedbackend.apps.core.authentication import exceptions as auth_ex
from sedbackend.apps.core.users import exceptions as user_ex
from sedbackend.apps.core.db import get_connection
import sedbackend.apps.cvs.project.exceptions as project_exceptions
from sedbackend.apps.cvs.vcs import models, storage, exceptions
from sedbackend.libs.datastructures.pagination import ListChunk
from sedbackend.apps.core.files import exceptions as file_ex


# ======================================================================================================================
# VCS
# ======================================================================================================================

def get_all_vcs(project_id: int) -> ListChunk[models.VCS]:
    try:
        with get_connection() as con:
            return storage.get_all_vcs(con, project_id)
    except project_exceptions.CVSProjectNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Could not find project with id={project_id}.',
        )


def get_vcs(project_id: int, vcs_id: int) -> models.VCS:
    try:
        with get_connection() as con:
            return storage.get_vcs(con, project_id, vcs_id)
    except exceptions.VCSNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Could not find VCS with id={vcs_id}.',
        )
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
    except project_exceptions.CVSProjectNoMatchException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'VCS with id={vcs_id} does not belong to project with id={project_id}.',
        )


def create_vcs(project_id: int, vcs_post: models.VCSPost) -> models.VCS:
    try:
        with get_connection() as con:
            result = storage.create_vcs(con, project_id, vcs_post)
            con.commit()
            return result
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
    except exceptions.VCSYearFromGreaterThanYearToException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Year from cannot be greater than year to.',
        )


def edit_vcs(project_id: int, vcs_id: int, vcs_post: models.VCSPost) -> models.VCS:
    try:
        with get_connection() as con:
            result = storage.edit_vcs(con, project_id, vcs_id, vcs_post)
            con.commit()
            return result
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
    except project_exceptions.CVSProjectNoMatchException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'VCS with id={vcs_id} does not belong to project with id={project_id}.',
        )
    except exceptions.VCSYearFromGreaterThanYearToException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Year from cannot be greater than year to.',
        )


def delete_vcs(user_id: int, project_id: int, vcs_id: int) -> bool:
    try:
        with get_connection() as con:
            res = storage.delete_vcs(con, user_id, project_id, vcs_id)
            con.commit()
            return res
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
    except project_exceptions.CVSProjectNoMatchException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'VCS with id={vcs_id} does not belong to project with id={project_id}.',
        )
    except file_ex.FileNotDeletedException:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"File could not be deleted"
        )
    except file_ex.PathMismatchException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Path to file does not match internal path'
        )


# ======================================================================================================================
# VCS Value driver
# ======================================================================================================================


def get_all_value_driver(user_id: int) -> List[models.ValueDriver]:
    try:
        with get_connection() as con:
            return storage.get_all_value_driver(con, user_id)
    except user_ex.UserNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Could not find user with id={user_id}.',
        )
    except exceptions.ValueDriverNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Could not find value drivers for user with id={user_id}'
        )


def get_all_value_driver_vcs(project_id: int, vcs_id: int) -> List[models.ValueDriver]:
    try:
        with get_connection() as con:
            res = storage.get_all_value_driver_vcs(con, project_id, vcs_id)
            con.commit()
            return res
    except exceptions.VCSNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Could not find vcs with id: {vcs_id}'
        )
    except exceptions.ValueDriverNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'Could not find value drivers'
        )
    except project_exceptions.CVSProjectNoMatchException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'VCS with id={vcs_id} does not belong to project with id={project_id}.',
        )


def get_all_value_drivers_vcs_row(project_id: int, vcs_id: int, row_id: int) -> List[models.ValueDriver]:
    try:
        with get_connection() as con:
            res = storage.get_all_value_drivers_vcs_row(con, project_id, vcs_id, row_id)
            con.commit()
            return res
    except exceptions.VCSNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Could not find vcs with id: {vcs_id}'
        )
    except exceptions.ValueDriverNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Could not find value drivers'
        )
    except project_exceptions.CVSProjectNoMatchException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'VCS with id={vcs_id} does not belong to project with id={project_id}.',
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


def create_value_driver(user_id: int, value_driver_post: models.ValueDriverPost) -> models.ValueDriver:
    try:
        with get_connection() as con:
            result = storage.create_value_driver(con, user_id, value_driver_post)
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


def delete_value_driver(project_id: int, value_driver_id: int) -> bool:
    try:
        with get_connection() as con:
            res = storage.delete_project_value_driver(con, project_id, value_driver_id)
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
    except exceptions.ProjectValueDriverNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Could not find project={project_id} <-> value driver={value_driver_id} relation.'
        )


def delete_all_value_drivers(user_id: int) -> bool:
    try:
        with get_connection() as con:
            res = storage.delete_all_value_drivers(con, user_id)
            con.commit()
            return res
    except exceptions.ValueDriverNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Could not find value driver with id={user_id}.',
        )
    except exceptions.ValueDriverFailedDeletionException:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'Failed to remove value driver with id={user_id}.',
        )
    except auth_ex.UnauthorizedOperationException:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Unauthorized user.',
        )


def add_vcs_multiple_needs_drivers(need_driver_ids: List[Tuple[int, int]]):
    try:
        with get_connection() as con:
            res = storage.add_vcs_multiple_needs_drivers(con, need_driver_ids)
            con.commit()
            return res
    except exceptions.GenericDatabaseException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Badly formatted request'
        )


def add_project_multiple_value_drivers(project_id: int, value_driver_ids: List[int]):
    try:
        with get_connection() as con:
            res = storage.add_project_value_drivers(con, project_id, value_driver_ids)
            con.commit()
            return res
    except exceptions.GenericDatabaseException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Badly formatted request'
        )
    except exceptions.ProjectValueDriverFailedToCreateException:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'Failed to create project={project_id} and value driver={value_driver_ids} relation'
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


def get_all_subprocess(project_id: int) -> List[models.VCSSubprocess]:
    try:
        with get_connection() as con:
            return storage.get_all_subprocess(con, project_id)
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


def get_subprocess(project_id: int, subprocess_id: int) -> models.VCSSubprocess:
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


def create_subprocess(project_id: int, subprocess_post: models.VCSSubprocessPost) -> models.VCSSubprocess:
    try:
        with get_connection() as con:
            result = storage.create_subprocess(con, project_id, subprocess_post)
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
    except exceptions.SubprocessNotUniqueException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Subprocess name must be unique.',
        )


def edit_subprocess(project_id: int, subprocess_id: int,
                    subprocess: models.VCSSubprocessPut) -> bool:
    try:
        with get_connection() as con:
            result = storage.edit_subprocess(con, project_id, subprocess_id, subprocess)
            con.commit()
            return result
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
    except exceptions.ISOProcessNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Could not find ISO process with id={subprocess.parent_process_id}.',
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


def delete_subprocess(project_int: int, subprocess_id: int) -> bool:
    try:
        with get_connection() as con:
            res = storage.delete_subprocess(con, project_int, subprocess_id)
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


# ======================================================================================================================
# VCS Table
# ======================================================================================================================


def get_vcs_table(project_id: int, vcs_id: int) -> List[models.VcsRow]:
    try:
        with get_connection() as con:
            return storage.get_vcs_table(con, project_id, vcs_id)
    except auth_ex.UnauthorizedOperationException:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Unauthorized user.',
        )
    except exceptions.VCSNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Could not find VCS with id={vcs_id}.',
        )
    except project_exceptions.CVSProjectNoMatchException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Project with id={project_id} does not match VCS with id={vcs_id}.',
        )


def edit_vcs_table(project_id: int, vcs_id: int, updated_vcs_rows: List[models.VcsRowPost]) -> bool:
    try:
        with get_connection() as con:
            res = storage.edit_vcs_table(con, project_id, vcs_id, updated_vcs_rows)
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
    except exceptions.VCSandVCSRowIDMismatchException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'The given vcs id does not match the vcs id of the vcs table'
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
    except exceptions.VCSStakeholderNeedFailedToUpdateException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Stakeholder need failed to update'
        )
    except project_exceptions.CVSProjectNoMatchException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Project with id={project_id} does not match VCS with id={vcs_id}.',
        )
    except exceptions.SubprocessFailedCreationException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Could not create subprocess'
        )
    except exceptions.VCSTableProcessNotUniqueException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Process name must be unique'
        )


# ======================================================================================================================
# VCS Duplicate
# ======================================================================================================================

def duplicate_vcs(project_id: int, vcs_id: int, n: int) -> List[models.VCS]:
    try:
        with get_connection() as con:
            res = storage.duplicate_whole_vcs(con, project_id, vcs_id, n)
            con.commit()
            return res
    except exceptions.VCSNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Could not find VCS'
        )

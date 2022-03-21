import os.path

from fastapi import HTTPException, status
from fastapi.logger import logger

from sedbackend.apps.core.db import get_connection
import sedbackend.apps.core.files.storage as storage
import sedbackend.apps.core.files.exceptions as exc
import sedbackend.apps.core.authentication.exceptions as exc_auth
import sedbackend.apps.core.files.models as models


def impl_save_file(file: models.StoredFilePost) -> models.StoredFileEntry:
    try:
        with get_connection() as con:
            res = storage.db_save_file(con, file)
            con.commit()
            return res
    except exc.FileSizeException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File is too big, and could not be saved."
        )


def impl_delete_file(file_id: int, current_user_id: int) -> bool:
    try:
        with get_connection() as con:
            res = storage.db_delete_file(con, file_id, current_user_id)
            con.commit()
            return res
    except exc.FileNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"No file with id = {file_id} could be found."
        )
    except exc_auth.UnauthorizedOperationException:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"User does not have access to a file with id = {file_id}"
        )


def impl_get_file_path(file_id: int, current_user_id: int) -> models.StoredFilePath:
    try:
        with get_connection() as con:
            stored_file_path = storage.db_get_file_path(con, file_id, current_user_id)

            # If we get this far, then the file is registered in the database.
            # We now need to assert that the file exists on disk.
            if os.path.exists(stored_file_path.path) is False:
                logger.error(f'File with id={file_id} at path="{stored_file_path.path}" '
                             f'is not available on drive, but exists in the database.')
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="The file is missing from persistent storage."
                )

            # If the file exists, then return the path
            return stored_file_path

    except exc.FileNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The requested file could not be found. It may have been deleted."
        )
    except exc_auth.UnauthorizedOperationException:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"User does not have access to a file with id = {file_id}"
        )


def impl_put_file_temp(file_id: int, temp: bool, current_user_id: int):
    try:
        with get_connection() as con:
            return storage.db_put_file_temp(con, file_id, temp, current_user_id)
    except exc.FileNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The requested file could not be found. It may have been deleted."
        )
    except exc_auth.UnauthorizedOperationException:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"User does not have access to a file with id = {file_id}"
        )


def impl_get_file(file_id: int, current_user_id: int):
    try:
        with get_connection() as con:
            file_path = storage.db_get_file_path(con, file_id, current_user_id)

    except exc.FileNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File could not be found."
        )
    except exc_auth.UnauthorizedOperationException:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User does not have access to requested file."
        )

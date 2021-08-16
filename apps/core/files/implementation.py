from fastapi import HTTPException, status

from apps.core.db import get_connection
import apps.core.files.storage as storage
import apps.core.files.exceptions as exc
import apps.core.authentication.exceptions as exc_auth
import apps.core.files.models as models


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


def impl_get_file_path(file_id: int, current_user_id: int):
    try:
        with get_connection() as con:
            return storage.db_get_file_path(con, file_id, current_user_id)
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

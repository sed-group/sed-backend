from typing import Any
from datetime import datetime
import os
from tempfile import SpooledTemporaryFile

from pydantic import BaseModel
from fastapi.datastructures import UploadFile


class StoredFilePost(BaseModel):
    filename: str
    owner_id: int
    extension: str
    file_object: Any

    @staticmethod
    def import_fastapi_file(file: UploadFile, current_user_id: int):
        filename = file.filename
        extension = os.path.splitext(file.filename)[1]
        return StoredFilePost(filename=filename,
                              extension=extension,
                              owner_id=current_user_id,
                              file_object=file.file)


class StoredFileEntry(BaseModel):
    id: int
    temp: bool
    filename: str
    insert_timestamp: datetime
    owner_id: int
    extension: str


class StoredFile(BaseModel):
    id: int
    temp: bool
    uuid: str
    filename: str
    insert_timestamp: datetime
    directory: str
    owner_id: int
    extension: str


class StoredFilePath(BaseModel):
    id: int
    filename: str
    path: str
    extension: str


class StoredFileReadout(BaseModel):
    id: int
    filename: str
    content: str

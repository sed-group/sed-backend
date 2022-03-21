import uuid
import shutil
import os

from mysql.connector.pooling import PooledMySQLConnection

import sedbackend.apps.core.files.models as models
import sedbackend.apps.core.files.exceptions as exc
from sedbackend.libs.mysqlutils import MySQLStatementBuilder, exclude_cols, FetchType

FILES_RELATIVE_UPLOAD_DIR = f'{os.path.abspath(os.sep)}sed_lab/uploaded_files/'
FILES_TABLE = 'files'
FILES_COLUMNS = ['id', 'temp', 'uuid', 'filename', 'insert_timestamp', 'directory', 'owner_id', 'extension']


def db_save_file(con: PooledMySQLConnection, file: models.StoredFilePost) -> models.StoredFileEntry:
    # Store file in filesystem
    filename_uuid = uuid.uuid4().hex
    path = FILES_RELATIVE_UPLOAD_DIR+filename_uuid
    with open(path, 'wb') as buffer:
        shutil.copyfileobj(file.file_object, buffer)

    # Store reference to file in database
    insert_stmnt = MySQLStatementBuilder(con)
    insert_stmnt.insert(FILES_TABLE, exclude_cols(FILES_COLUMNS, ['id', 'insert_timestamp']))\
        .set_values([True, filename_uuid, file.filename, FILES_RELATIVE_UPLOAD_DIR, file.owner_id, file.extension])\
        .execute()

    file_id = insert_stmnt.last_insert_id

    return db_get_file_entry(con, file_id, file.owner_id)


def db_delete_file(con: PooledMySQLConnection, file_id: int, current_user_id: int) -> bool:
    return True


def db_get_file_entry(con: PooledMySQLConnection, file_id: int, current_user_id: int) -> models.StoredFileEntry:
    select_stmnt = MySQLStatementBuilder(con)
    res = select_stmnt.select(FILES_TABLE, exclude_cols(FILES_COLUMNS, ['uuid', 'directory']))\
        .where('id = ?', [file_id])\
        .execute(dictionary=True, fetch_type=FetchType.FETCH_ONE)

    if res is None:
        raise exc.FileNotFoundException

    stored_file = models.StoredFileEntry(**res)
    return stored_file


def db_get_file_path(con: PooledMySQLConnection, file_id: int, current_user_id: int) -> models.StoredFilePath:
    select_stmnt = MySQLStatementBuilder(con)
    res = select_stmnt\
        .select(FILES_TABLE, ['filename', 'uuid', 'directory', 'extension'])\
        .where('id=?', [file_id])\
        .execute(dictionary=True, fetch_type=FetchType.FETCH_ONE)

    if res is None:
        raise exc.FileNotFoundException('File not found in DB')

    path = res['directory'] + res['uuid']
    stored_path = models.StoredFilePath(id=file_id, filename=res['filename'], path=path, extension=res['extension'])
    return stored_path


def db_put_file_temp(con: PooledMySQLConnection, file_id: int, temp: bool, current_user_id: int) \
        -> models.StoredFileEntry:
    pass


def db_put_filename(con: PooledMySQLConnection, file_id: int, filename_new: str, current_user_id: int) \
        -> models.StoredFileEntry:
    pass

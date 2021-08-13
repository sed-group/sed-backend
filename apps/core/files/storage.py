import uuid
import shutil
import os

from mysql.connector.pooling import PooledMySQLConnection

import apps.core.files.models as models
import apps.core.files.exceptions as exc
from libs.mysqlutils import MySQLStatementBuilder, exclude_cols, FetchType

FILES_TABLE = 'files'
FILES_COLUMNS = ['id', 'temp', 'path', 'filename', 'insert_timestamp', 'directory', 'owner_id', 'extension']


def db_save_file(con: PooledMySQLConnection, file: models.StoredFilePost) -> models.StoredFileEntry:
    # Store file in filesystem
    root = os.path.abspath(os.sep)
    directory = root + 'sed_lab/uploaded_files/'
    filename_unique = uuid.uuid4().hex
    path = directory+filename_unique
    with open(f'{directory}{filename_unique}', 'wb') as buffer:
        shutil.copyfileobj(file.file_object, buffer)

    # Store reference to file in database
    insert_stmnt = MySQLStatementBuilder(con)
    insert_stmnt.insert(FILES_TABLE, exclude_cols(FILES_COLUMNS, ['id', 'insert_timestamp']))\
        .set_values([True, path, file.filename, directory, file.owner_id, file.extension])\
        .execute()

    file_id = insert_stmnt.last_insert_id

    return db_get_file_entry(con, file_id, file.owner_id)


def db_delete_file(con: PooledMySQLConnection, file_id: int, current_user_id: int) -> bool:
    return True


def db_get_file_entry(con: PooledMySQLConnection, file_id: int, current_user_id: int) -> models.StoredFileEntry:
    select_stmnt = MySQLStatementBuilder(con)
    res = select_stmnt.select(FILES_TABLE, exclude_cols(FILES_COLUMNS, ['path', 'directory']))\
        .where('id = ?', [file_id])\
        .execute(dictionary=True, fetch_type=FetchType.FETCH_ONE)

    if res is None:
        raise exc.FileNotFoundException

    stored_file = models.StoredFileEntry(**res)
    return stored_file



def db_get_file(con: PooledMySQLConnection, file_id: int, current_user_id: int):
    pass


def db_put_file_temp(con: PooledMySQLConnection, file_id: int, temp: bool, current_user_id: int) \
        -> models.StoredFileEntry:
    pass


def db_put_filename(con: PooledMySQLConnection, file_id: int, filename_new: str, current_user_id: int) \
        -> models.StoredFileEntry:
    pass

import uuid
import shutil
import os

from mysql.connector.pooling import PooledMySQLConnection
from fastapi.logger import logger
import os

import sedbackend.apps.core.files.models as models
import sedbackend.apps.core.files.exceptions as exc
import sedbackend.apps.core.files.implementation as impl
from mysqlsb import MySQLStatementBuilder, exclude_cols, FetchType

FILES_RELATIVE_UPLOAD_DIR = f'{os.path.abspath(os.sep)}sed_lab/uploaded_files/'
FILES_TABLE = 'files'
FILES_TO_SUBPROJECTS_MAP_TABLE = 'files_subprojects_map'
FILES_COLUMNS = ['id', 'temp', 'uuid', 'filename', 'insert_timestamp', 'directory', 'owner_id', 'extension']
FILES_TO_SUBPROJECTS_MAP_COLUMNS = ['id', 'file_id', 'subproject_id']


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

    # Store mapping between file id and subproject id in database
    insert_mapping_stmnt = MySQLStatementBuilder(con)
    insert_mapping_stmnt.insert(FILES_TO_SUBPROJECTS_MAP_TABLE, ['file_id', 'subproject_id'])\
        .set_values([file_id, file.subproject_id])\
        .execute()

    return db_get_file_entry(con, file_id, file.owner_id)


def db_delete_file(con: PooledMySQLConnection, file_id: int, current_user_id: int) -> bool:
    stored_file_path = impl.impl_get_file_path(file_id, current_user_id)
    
    if os.path.commonpath([FILES_RELATIVE_UPLOAD_DIR]) != os.path.commonpath([FILES_RELATIVE_UPLOAD_DIR, os.path.abspath(stored_file_path.path)]):
        raise exc.PathMismatchException
        
    try:
        os.remove(stored_file_path.path)
        delete_stmnt = MySQLStatementBuilder(con)
        delete_stmnt.delete(FILES_TABLE) \
            .where('id=?', [file_id]) \
            .execute(fetch_type=FetchType.FETCH_NONE)
            
    except Exception:
        raise exc.FileNotDeletedException

    return True


def db_get_file_entry(con: PooledMySQLConnection, file_id: int, current_user_id: int) -> models.StoredFileEntry:
    res_dict = None
    with con.cursor(prepared=True) as cursor:
        # This expression uses two tables (files and files_to_subprojects_map)
        query = f"SELECT {', '.join(['f.id', 'f.temp', 'f.uuid', 'f.filename', 'f.insert_timestamp', 'f.directory', 'f.owner_id', 'f.extension'])}, fsm.`subproject_id` " \
                f"FROM `{FILES_TABLE}` f " \
                f"INNER JOIN {FILES_TO_SUBPROJECTS_MAP_TABLE} fsm ON (f.id = fsm.file_id) " \
                f"WHERE f.`id` = ?"
        values = [file_id]

        # Log for sanity-check
        logger.debug(f"db_get_file_entry query: '{query}' with values: {values}")

        # Execute query
        cursor.execute(query, values)

        # Handle results
        results = cursor.fetchone()

        if results is None:
            raise exc.FileNotFoundException

        res_dict = dict(zip(cursor.column_names, results))

    stored_file = models.StoredFileEntry(**res_dict)
    return stored_file


def db_get_file_path(con: PooledMySQLConnection, file_id: int, current_user_id: int) -> models.StoredFilePath:
    select_stmnt = MySQLStatementBuilder(con)
    res = select_stmnt\
        .select(FILES_TABLE, ['filename', 'uuid', 'directory', 'owner_id', 'extension'])\
        .where('id=?', [file_id])\
        .execute(dictionary=True, fetch_type=FetchType.FETCH_ONE)

    if res is None:
        raise exc.FileNotFoundException('File not found in DB')

    path = res['directory'] + res['uuid']
    stored_path = models.StoredFilePath(
        id=file_id, filename=res['filename'], path=path, owner_id=res['owner_id'], extension=res['extension'])
    return stored_path


def db_put_file_temp(con: PooledMySQLConnection, file_id: int, temp: bool, current_user_id: int) \
        -> models.StoredFileEntry:
    pass


def db_put_filename(con: PooledMySQLConnection, file_id: int, filename_new: str, current_user_id: int) \
        -> models.StoredFileEntry:
    pass


def db_get_file_mapped_subproject_id(con: PooledMySQLConnection, file_id) -> int:
    select_stmnt = MySQLStatementBuilder(con)
    res = select_stmnt.select(FILES_TO_SUBPROJECTS_MAP_TABLE, ['subproject_id'])\
        .where('file_id=?', [file_id])\
        .execute(dictionary=True, fetch_type=FetchType.FETCH_ONE)

    if res is None:
        raise exc.SubprojectMappingNotFound('Mapping could not be found.')

    return res['subproject_id']

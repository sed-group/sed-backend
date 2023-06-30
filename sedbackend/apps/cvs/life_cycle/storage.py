from typing import List

from fastapi import UploadFile
from fastapi.logger import logger
from mysql.connector.pooling import PooledMySQLConnection

from mysqlsb import MySQLStatementBuilder, FetchType, Sort

from sedbackend.apps.core.files.models import StoredFilePath
from sedbackend.apps.cvs.life_cycle import exceptions, models
from sedbackend.apps.cvs.vcs import storage as vcs_storage, exceptions as vcs_exceptions
from sedbackend.apps.core.files import models as file_models, storage as file_storage, exceptions as file_ex
from sedbackend.apps.core.projects import storage as core_project_storage
from mysql.connector import Error
import magic
import pandas as pd

CVS_NODES_TABLE = 'cvs_nodes'
CVS_NODES_COLUMNS = ['cvs_nodes.id', 'vcs', 'from', 'to', 'pos_x', 'pos_y']

CVS_PROCESS_NODES_TABLE = 'cvs_process_nodes'
CVS_PROCESS_NODES_COLUMNS = CVS_NODES_COLUMNS + ['vcs_row']

CVS_START_STOP_NODES_TABLE = 'cvs_start_stop_nodes'
CVS_START_STOP_NODES_COLUMNS = CVS_NODES_COLUMNS + ['type']

CVS_DSM_FILES_TABLE = 'cvs_dsm_files'
CVS_DSM_FILES_COLUMNS = ['vcs_id', 'file_id']

MAX_FILE_SIZE = 100 * 10 ** 6  # 100MB


def populate_process_node(db_connection, project_id, result) -> models.ProcessNodeGet:
    logger.debug(f'Populating model for process node with id={result["id"]} ')

    return models.ProcessNodeGet(
        id=result['id'],
        vcs_id=result['vcs'],
        from_node=result['from'],
        to_node=result['to'],
        pos_x=result['pos_x'],
        pos_y=result['pos_y'],
        vcs_row=vcs_storage.get_vcs_row(
            db_connection, project_id, result['vcs_row'])
    )


def populate_start_stop_node(result) -> models.StartStopNodeGet:
    logger.debug(
        f'Populating model for start/stop node with id={result["id"]}')
    return models.StartStopNodeGet(
        id=result['id'],
        vcs_id=result['vcs'],
        from_node=result['from'],
        to_node=result['to'],
        pos_x=result['pos_x'],
        pos_y=result['pos_y'],
        type=result['type']
    )


def get_node(db_connection: PooledMySQLConnection, project_id: int, node_id: int, table=CVS_NODES_TABLE,
             columns=None) -> dict:
    if columns is None:
        columns = CVS_NODES_COLUMNS
    select_statement = MySQLStatementBuilder(db_connection)
    try:
        result = select_statement \
            .select(table, columns) \
            .where('id = %s', [node_id]) \
            .execute(fetch_type=FetchType.FETCH_ONE, dictionary=True)

    except Error as e:
        logger.debug(f'Error msg: {e.msg}')
        raise exceptions.NodeNotFoundException

    # Check if vcs exists and matches project id
    vcs_storage.get_vcs(db_connection, result['vcs'], project_id)

    return result


def get_process_node(db_connection: PooledMySQLConnection, project_id: int, node_id: int) -> models.ProcessNodeGet:
    logger.debug(f'Fetching a process node with id={node_id}.')

    select_statement = MySQLStatementBuilder(db_connection)
    try:
        result = select_statement \
            .select(CVS_PROCESS_NODES_TABLE, CVS_PROCESS_NODES_COLUMNS) \
            .inner_join(CVS_NODES_TABLE, 'cvs_nodes.id = cvs_process_nodes.id') \
            .where('cvs_nodes.id = %s', [node_id]) \
            .execute(fetch_type=FetchType.FETCH_ONE, dictionary=True)

    except Error as e:
        logger.debug(f'Error msg: {e.msg}')
        raise exceptions.NodeNotFoundException

    return populate_process_node(db_connection, project_id, result)


def get_start_stop_node(db_connection: PooledMySQLConnection, node_id: int) -> models.StartStopNodeGet:
    logger.debug(f'Fetching a process node with id={node_id}.')

    select_statement = MySQLStatementBuilder(db_connection)
    try:
        result = select_statement \
            .select(CVS_START_STOP_NODES_TABLE, CVS_START_STOP_NODES_COLUMNS) \
            .inner_join(CVS_NODES_TABLE, 'cvs_nodes.id = cvs_start_stop_nodes.id') \
            .where('cvs_nodes.id = %s', [node_id]) \
            .execute(fetch_type=FetchType.FETCH_ONE, dictionary=True)

    except Error as e:
        logger.debug(f'Error msg: {e.msg}')
        raise exceptions.NodeNotFoundException

    return populate_start_stop_node(result)


# Create parent node and return id
def create_node(db_connection: PooledMySQLConnection, vcs_id: int, node: models.NodePost) -> int:
    columns = ['vcs', 'pos_x', 'pos_y']
    values = [vcs_id, node.pos_x, node.pos_y]

    node_id = None
    try:
        insert_statement = MySQLStatementBuilder(db_connection)
        insert_statement \
            .insert(table=CVS_NODES_TABLE, columns=columns) \
            .set_values(values) \
            .execute(fetch_type=FetchType.FETCH_NONE)
        node_id = insert_statement.last_insert_id
    except Error as e:
        logger.debug(f'Error msg: {e.msg}')
        if vcs_id is not None:
            raise vcs_exceptions.VCSNotFoundException

    logger.debug('Created standard node')
    return node_id


def create_process_node(db_connection: PooledMySQLConnection, project_id: int, vcs_id: int,
                        node: models.ProcessNodePost) -> models.ProcessNodeGet:
    logger.debug(f'Create a process node for vcs with id={vcs_id}.')

    node_id = create_node(db_connection, vcs_id, node)

    try:
        insert_statement = MySQLStatementBuilder(db_connection)
        insert_statement \
            .insert(table=CVS_PROCESS_NODES_TABLE, columns=['id', 'vcs_row']) \
            .set_values([node_id, node.vcs_row_id]) \
            .execute(fetch_type=FetchType.FETCH_NONE, return_affected_rows=True)
        # node_id = insert_statement.last_insert_id
        logger.debug(f'Finished process node creation with node id {node_id}')
    except Error as e:
        logger.debug(f'Error msg: {e.msg}')
        raise vcs_exceptions.VCSNotFoundException

    logger.debug('Before getting process node')
    return get_process_node(db_connection, project_id, node_id)


def create_start_stop_node(db_connection: PooledMySQLConnection, node: models.StartStopNodePost,
                           vcs_id: int) -> models.StartStopNodeGet:
    logger.debug(f'Create a process node for vcs with id={vcs_id}.')

    node_id = create_node(db_connection, node, vcs_id)

    columns = ['id', 'type']
    values = [node_id, node.type]

    insert_statement = MySQLStatementBuilder(db_connection)
    try:
        insert_statement \
            .insert(table=CVS_START_STOP_NODES_TABLE, columns=columns) \
            .set_values(values) \
            .execute(fetch_type=FetchType.FETCH_NONE)
    except Error as e:
        logger.debug(f'Error msg: {e.msg}')
        if node.type != "start" and node.type != "stop":
            raise exceptions.InvalidNodeType
        elif vcs_id is not None:
            raise vcs_exceptions.VCSNotFoundException

    return get_start_stop_node(db_connection, node_id)


def delete_node(db_connection: PooledMySQLConnection, project_id: int, node_id: int) -> bool:
    logger.debug(f'Delete node with id={node_id}.')

    # Check if node exists and matches project id
    get_node(db_connection, project_id, node_id)

    delete_statement = MySQLStatementBuilder(db_connection)
    _, rows = delete_statement.delete(CVS_NODES_TABLE) \
        .where('id = %s', [node_id]) \
        .execute(return_affected_rows=True)

    if rows == 0:
        raise exceptions.NodeFailedDeletionException(node_id)

    return True


def update_node(db_connection: PooledMySQLConnection, project_id: int, node_id: int, node: models.NodePost) -> bool:
    logger.debug(f'Updating node with id={node_id}.')

    # Performs necessary checks
    get_node(db_connection, project_id, node_id)

    update_statement = MySQLStatementBuilder(db_connection)
    update_statement.update(
        table=CVS_NODES_TABLE,
        set_statement='pos_x = %s, pos_y = %s',
        values=[node.pos_x, node.pos_y],
    )
    update_statement.where('id = %s', [node_id])
    _, rows = update_statement.execute(return_affected_rows=True)
    if rows == 0:
        raise exceptions.NodeFailedToUpdateException

    return True


def get_bpmn(db_connection: PooledMySQLConnection, project_id: int, vcs_id: int) -> models.BPMNGet:
    logger.debug(f'Get BPMN for vcs with id={vcs_id}.')

    # Check if vcs exists and matches project id
    vcs_storage.get_vcs(db_connection, project_id, vcs_id)

    where_statement = f'vcs = %s'
    where_values = [vcs_id]

    try:
        select_statement = MySQLStatementBuilder(db_connection)
        process_nodes_result = select_statement \
            .select(CVS_PROCESS_NODES_TABLE, CVS_PROCESS_NODES_COLUMNS) \
            .inner_join(CVS_NODES_TABLE, 'cvs_nodes.id = cvs_process_nodes.id') \
            .where(where_statement, where_values) \
            .order_by(['cvs_nodes.id'], Sort.ASCENDING) \
            .execute(fetch_type=FetchType.FETCH_ALL, dictionary=True)
        process_nodes = [populate_process_node(
            db_connection, project_id, result) for result in process_nodes_result]

        select_statement = MySQLStatementBuilder(db_connection)
        # start_stop_nodes_result = \
        select_statement \
            .select(CVS_START_STOP_NODES_TABLE, CVS_START_STOP_NODES_COLUMNS) \
            .inner_join(CVS_NODES_TABLE, 'cvs_nodes.id = cvs_start_stop_nodes.id') \
            .where(where_statement, where_values) \
            .order_by(['cvs_nodes.id'], Sort.ASCENDING) \
            .execute(fetch_type=FetchType.FETCH_ALL, dictionary=True)
        # start_stop_nodes = [populate_start_stop_node(result) for result in start_stop_nodes_result]
    except Error as e:
        logger.debug(f'Error msg: {e.msg}')
        raise vcs_exceptions.VCSNotFoundException

    return models.BPMNGet(
        nodes=process_nodes
        # [*process_nodes, *start_stop_nodes]
    )


def update_bpmn(db_connection: PooledMySQLConnection, project_id: int, vcs_id: int,
                bpmn: models.BPMNGet) -> bool:
    logger.debug(f'Updating bpmn with vcs id={vcs_id}.')

    # Check if vcs exists and matches project id
    vcs_storage.get_vcs(db_connection, project_id, vcs_id)

    for node in bpmn.nodes:
        updated_node = models.NodePost(
            pos_x=node.pos_x,
            pos_y=node.pos_y
        )
        update_node(db_connection, project_id, node.id, updated_node)

    return True


def save_dsm_file(db_connection: PooledMySQLConnection, application_sid, project_id: int,
                  vcs_id: int, file: UploadFile, user_id) -> bool:
    subproject = core_project_storage.db_get_subproject_native(db_connection, application_sid, project_id)

    model_file = file_models.StoredFilePost.import_fastapi_file(file, user_id, subproject.id)

    if model_file.extension != ".csv":
        raise exceptions.InvalidFileTypeException

    try:
        file_id = get_dsm_file_id(db_connection, project_id, vcs_id)
        if file_id is not None:
            file_storage.db_delete_file(db_connection, file_id, user_id)
    except file_ex.FileNotFoundException:
        pass  # File doesn't exist, so we don't need to delete it
    except Exception:
        try:
            # File does not exist in persistent storage but exists in database
            delete_statement = MySQLStatementBuilder(db_connection)
            _, rows = delete_statement.delete(CVS_DSM_FILES_TABLE) \
                .where('vcs_id = %s', [vcs_id]) \
                .execute(return_affected_rows=True)
        except:
            pass

    with model_file.file_object as f:
        f.seek(0)
        tmp_file = f.read()
        mime = magic.from_buffer(tmp_file)
        logger.debug(mime)
        # TODO doesn't work with windows if we create the file in excel.
        if mime != "CSV text" and mime != "ASCII text":
            raise exceptions.InvalidFileTypeException

        if f.tell() > MAX_FILE_SIZE:
            raise exceptions.FileSizeException

        f.seek(0)
        dsm_file = pd.read_csv(f)
        logger.debug(f'File content: {dsm_file}')
        vcs_table = vcs_storage.get_vcs_table(db_connection, project_id, vcs_id)

        vcs_processes = [row.iso_process.name if row.iso_process is not None else
                         row.subprocess.name for row in vcs_table]

        for process in dsm_file['Processes'].values[1:-1]:
            if process not in vcs_processes:
                raise exceptions.ProcessesVcsMatchException

        f.seek(0)
        stored_file = file_storage.db_save_file(db_connection, model_file)

    insert_statement = MySQLStatementBuilder(db_connection)
    insert_statement.insert(CVS_DSM_FILES_TABLE, CVS_DSM_FILES_COLUMNS) \
        .set_values([vcs_id, stored_file.id]) \
        .execute(fetch_type=FetchType.FETCH_NONE)

    return True


def get_dsm_file_id(db_connection: PooledMySQLConnection, project_id: int, vcs_id: int) -> int:
    vcs_storage.get_vcs(db_connection, project_id, vcs_id)  # Check if vcs exists and matches project id

    select_statement = MySQLStatementBuilder(db_connection)
    file_res = select_statement.select(CVS_DSM_FILES_TABLE, CVS_DSM_FILES_COLUMNS) \
        .where('vcs_id = %s', [vcs_id]) \
        .execute(fetch_type=FetchType.FETCH_ONE, dictionary=True)

    if file_res is None:
        raise file_ex.FileNotFoundException

    return file_res['file_id']


def get_multiple_dsm_file_id(db_connection: PooledMySQLConnection, vcs_ids: List[int]) -> int:
    select_statement = MySQLStatementBuilder(db_connection)
    file_res = select_statement.select(CVS_DSM_FILES_TABLE, CVS_DSM_FILES_COLUMNS) \
        .where(",".join(["%s" for _ in range(len(vcs_ids))]), vcs_ids) \
        .execute(fetch_type=FetchType.FETCH_ONE, dictionary=True)

    if file_res is None:
        raise file_ex.FileNotFoundException

    return file_res['file_id']


def get_dsm_file_path(db_connection: PooledMySQLConnection, project_id: int, vcs_id: int, user_id) -> StoredFilePath:
    file_id = get_dsm_file_id(db_connection, project_id, vcs_id)
    return file_storage.db_get_file_path(db_connection, file_id, user_id)


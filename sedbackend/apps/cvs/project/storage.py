from fastapi.logger import logger
from mysql.connector.pooling import PooledMySQLConnection

from sedbackend.apps.core.authentication import exceptions as auth_exceptions
from sedbackend.apps.core.users.storage import db_get_user_safe_with_id
from sedbackend.apps.cvs.project import models as models, exceptions as exceptions
from sedbackend.libs.datastructures.pagination import ListChunk
from sedbackend.libs.mysqlutils import MySQLStatementBuilder, Sort, FetchType
import sedbackend.apps.core.projects.models as proj_models
import sedbackend.apps.core.projects.storage as proj_storage

CVS_APPLICATION_SID = "MOD.CVS"
CVS_PROJECT_TABLE = 'cvs_projects'
CVS_PROJECT_COLUMNS = ['id', 'name', 'description', 'currency', 'owner_id', 'datetime_created']


def get_all_cvs_project(db_connection: PooledMySQLConnection, user_id: int) -> ListChunk[models.CVSProject]:
    logger.debug(f'Fetching all CVS projects for user with id={user_id}.')

    where_statement = f'owner_id = %s'
    where_values = [user_id]

    select_statement = MySQLStatementBuilder(db_connection)
    results = select_statement.select(CVS_PROJECT_TABLE, CVS_PROJECT_COLUMNS) \
        .where(where_statement, where_values) \
        .order_by(['id'], Sort.ASCENDING) \
        .execute(fetch_type=FetchType.FETCH_ALL, dictionary=True)

    project_list = []
    for result in results:
        project_list.append(populate_cvs_project(db_connection, result))

    count_statement = MySQLStatementBuilder(db_connection)
    result = count_statement.count(CVS_PROJECT_TABLE) \
        .where(where_statement, where_values) \
        .execute(fetch_type=FetchType.FETCH_ONE, dictionary=True)
    chunk = ListChunk[models.CVSProject](chunk=project_list, length_total=result['count'])

    return chunk


def get_cvs_project(db_connection: PooledMySQLConnection, project_id: int) -> models.CVSProject:
    logger.debug(f'Fetching CVS project with id={project_id}.')

    select_statement = MySQLStatementBuilder(db_connection)
    result = select_statement \
        .select(CVS_PROJECT_TABLE, CVS_PROJECT_COLUMNS) \
        .where('id = %s', [project_id]) \
        .execute(fetch_type=FetchType.FETCH_ONE, dictionary=True)

    if result is None:
        raise exceptions.CVSProjectNotFoundException

    return populate_cvs_project(db_connection, result)


def create_cvs_project(db_connection: PooledMySQLConnection, project: models.CVSProjectPost,
                       user_id: int) -> models.CVSProject:
    logger.debug(f'Creating a CVS project for user with id={user_id}.')

    insert_statement = MySQLStatementBuilder(db_connection)
    insert_statement \
        .insert(table=CVS_PROJECT_TABLE, columns=['name', 'description', 'currency', 'owner_id']) \
        .set_values([project.name, project.description, project.currency, user_id]) \
        .execute(fetch_type=FetchType.FETCH_NONE)

    cvs_project_id = insert_statement.last_insert_id

    # Insert corresponding subproject row
    subproject = proj_models.SubProjectPost(application_sid=CVS_APPLICATION_SID, native_project_id=cvs_project_id)
    proj_storage.db_post_subproject(db_connection, subproject, user_id)

    return get_cvs_project(db_connection, cvs_project_id)


def edit_cvs_project(db_connection: PooledMySQLConnection, project_id: int,
                     new_project: models.CVSProjectPost) -> models.CVSProject:
    logger.debug(f'Editing CVS project with id={project_id}.')

    old_project = get_cvs_project(db_connection, project_id)

    if (old_project.name, old_project.description) == (new_project.name, new_project.description):
        # No change
        return old_project

    # Updating
    update_statement = MySQLStatementBuilder(db_connection)
    update_statement.update(
        table=CVS_PROJECT_TABLE,
        set_statement='name = %s, description = %s, currency = %s',
        values=[new_project.name, new_project.description, new_project.currency],
    )
    update_statement.where('id = %s', [project_id])
    _, rows = update_statement.execute(return_affected_rows=True)

    if rows == 0:
        raise exceptions.CVSProjectFailedToUpdateException

    return get_cvs_project(db_connection, project_id)


def delete_cvs_project(db_connection: PooledMySQLConnection, project_id: int, user_id: int) -> bool:
    logger.debug(f'Deleting CVS project with id={project_id}.')

    delete_statement = MySQLStatementBuilder(db_connection)
    _, rows = delete_statement.delete(CVS_PROJECT_TABLE) \
        .where('id = %s', [project_id]) \
        .execute(return_affected_rows=True)

    if rows == 0:
        raise exceptions.CVSProjectFailedDeletionException

    return True


def populate_cvs_project(db_connection: PooledMySQLConnection,
                         db_result) -> models.CVSProject:
    return models.CVSProject(
        id=db_result['id'],
        name=db_result['name'],
        description=db_result['description'],
        currency=db_result['currency'],
        owner=db_get_user_safe_with_id(db_connection, db_result['owner_id']),
        datetime_created=db_result['datetime_created'],
    )

from fastapi import Depends
from fastapi.logger import logger
from mysql.connector.pooling import PooledMySQLConnection

from sedbackend.apps.core.authentication import exceptions as auth_exceptions
from sedbackend.apps.core.authentication.utils import get_current_active_user
from sedbackend.apps.core.users.models import User
from sedbackend.apps.core.users.storage import db_get_user_safe_with_id
from sedbackend.apps.cvs.project import models as models, exceptions as exceptions
from sedbackend.libs.datastructures.pagination import ListChunk
from mysqlsb import MySQLStatementBuilder, Sort, FetchType
import sedbackend.apps.core.projects.models as proj_models
import sedbackend.apps.core.projects.storage as proj_storage

CVS_APPLICATION_SID = "MOD.CVS"
CVS_PROJECT_TABLE = 'cvs_projects'
CVS_PROJECT_COLUMNS = ['id', 'name', 'description', 'currency', 'owner_id', 'datetime_created']


def get_all_cvs_project(db_connection: PooledMySQLConnection, user_id: int) -> ListChunk[models.CVSProject]:
    logger.debug(f'Fetching all CVS projects for user with id={user_id}.')

    query = f'SELECT DISTINCT p.*, COALESCE(pp.access_level, 4) AS my_access_right \
            FROM cvs_projects p \
            LEFT JOIN projects_subprojects ps ON p.id = ps.project_id AND ps.owner_id = %s \
            LEFT JOIN projects_participants pp ON p.id = pp.project_id AND pp.user_id = %s \
            WHERE p.owner_id = %s OR ps.owner_id = %s OR pp.user_id = %s;'

    with db_connection.cursor(prepared=True, dictionary=True) as cursor:
        cursor.execute(query, [user_id, user_id, user_id, user_id, user_id])
        result = cursor.fetchall()

    cvs_project_list = [populate_cvs_project(db_connection, res) for res in result]

    return ListChunk[models.CVSProject](chunk=cvs_project_list, length_total=len(cvs_project_list))


def get_cvs_project(db_connection: PooledMySQLConnection, project_id: int, user_id: int) -> models.CVSProject:
    logger.debug(f'Fetching CVS project with id={project_id} user={user_id}.')

    query = f'SELECT p.*, COALESCE(pp.access_level, 4) AS my_access_right \
            FROM cvs_projects p \
            LEFT JOIN projects_participants pp ON pp.project_id = %s AND pp.user_id = %s \
            WHERE p.id = %s;'

    with db_connection.cursor(prepared=True, dictionary=True) as cursor:
        cursor.execute(query, [project_id, user_id, project_id])
        result = cursor.fetchone()
    logger.debug(result)
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
    subproject = proj_models.SubProjectPost(name=project.name, application_sid=CVS_APPLICATION_SID, native_project_id=cvs_project_id)
    proj_storage.db_post_subproject(db_connection, subproject, user_id)

    return get_cvs_project(db_connection, cvs_project_id, user_id)


def edit_cvs_project(db_connection: PooledMySQLConnection, project_id: int,
                     new_project: models.CVSProjectPost, user_id: int) -> models.CVSProject:
    logger.debug(f'Editing CVS project with id={project_id}.')

    # Updating
    update_statement = MySQLStatementBuilder(db_connection)
    update_statement.update(
        table=CVS_PROJECT_TABLE,
        set_statement='name = %s, description = %s, currency = %s',
        values=[new_project.name, new_project.description, new_project.currency],
    )
    update_statement.where('id = %s', [project_id])
    update_statement.execute(return_affected_rows=True)

    return get_cvs_project(db_connection, project_id, user_id)


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
    logger.debug(f'Populating cvs project with {db_result}')
    return models.CVSProject(
        id=db_result['id'],
        name=db_result['name'],
        description=db_result['description'],
        currency=db_result['currency'],
        owner=db_get_user_safe_with_id(db_connection, db_result['owner_id']),
        datetime_created=db_result['datetime_created'],
        my_access_right=db_result['my_access_right']
    )

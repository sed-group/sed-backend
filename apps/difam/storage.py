from typing import List

from mysql.connector.pooling import PooledMySQLConnection

import apps.difam.models as models
import apps.difam.exceptions as exceptions
from apps.core.projects.storage import db_get_user_subprojects_with_application_sid
from libs.mysqlutils import MySQLStatementBuilder, FetchType, Sort, exclude_cols

DIFAM_APPLICATION_SID = "MOD.DIFAM"
DIFAM_TABLE = "difam_projects"
DIFAM_COLUMNS = ["id", "name", "individual_archetype_id", "owner_id", "datetime_created"]


def db_put_project_archetype(con, difam_project_id, individual_archetype_id: int):
    update_stmnt = MySQLStatementBuilder(con)
    res, rows = update_stmnt\
        .update(DIFAM_TABLE, "individual_archetype_id = %s", [individual_archetype_id])\
        .where("id = %s", [difam_project_id])\
        .execute(fetch_type=FetchType.FETCH_NONE, return_affected_rows=True)

    if rows == 0:
        raise exceptions.DifamProjectFailedToUpdateException(f"Update did not occur for project with id = {difam_project_id}.")

    return db_get_difam_project(con, difam_project_id)


def db_post_difam_project(con: PooledMySQLConnection, difam_project: models.DifamProjectPost, current_user_id: int) \
        -> models.DifamProject:

    # TODO: Check if archetype exists

    insert_stmnt = MySQLStatementBuilder(con)
    insert_stmnt\
        .insert(DIFAM_TABLE, ['name', 'individual_archetype_id', 'owner_id'])\
        .set_values([difam_project.name,
                     difam_project.individual_archetype_id,
                     current_user_id])\
        .execute(fetch_type=FetchType.FETCH_NONE)

    project_id = insert_stmnt.last_insert_id

    return db_get_difam_project(con, project_id)


def db_get_difam_project(con: PooledMySQLConnection, difam_project_id: int) -> models.DifamProject:
    select_stmnt = MySQLStatementBuilder(con)
    res = select_stmnt\
        .select(DIFAM_TABLE, DIFAM_COLUMNS).where("id = %s", [difam_project_id])\
        .execute(fetch_type=FetchType.FETCH_ONE, dictionary=True)

    if res is None:
        raise exceptions.DifamProjectNotFoundException(f"No DIFAM project found with ID = {difam_project_id}")

    return models.DifamProject(**res)


def db_get_difam_projects(con: PooledMySQLConnection, segment_length: int, index: int, current_user_id: int) \
        -> List[models.DifamProject]:
    """
    Returns list of projects in which the current user is a participant.
    :param con: Connection
    :param segment_length: Max amount of rows returned
    :param index: Offset, allowing pagination
    :param current_user_id: ID of current user
    :return:
    """

    subproject_list = db_get_user_subprojects_with_application_sid(con, current_user_id, DIFAM_APPLICATION_SID)

    difam_project_id_list = []
    for subproject in subproject_list:
        difam_project_id_list.append(subproject.native_project_id)

    # Ensure that all projects in which the user is a participant is fetched,
    # as well as all the projects in which the user is an owner. This ensures that DIFAM projects
    # which do not have an associated project also shows up in the list, as long as the user is the owner.
    # This is useful, because users might want to create DIFAM projects, without having to create a "Core Project"
    if len(difam_project_id_list) > 0:
        where_stmnt = f"id IN {MySQLStatementBuilder.placeholder_array(len(difam_project_id_list))} OR owner_id = %s"
    else:
        where_stmnt = f"owner_id = %s"

    where_values = difam_project_id_list.copy()
    where_values.append(current_user_id)

    select_stmnt = MySQLStatementBuilder(con)
    rs = select_stmnt.select(DIFAM_TABLE, DIFAM_COLUMNS)\
        .where(where_stmnt, where_values)\
        .order_by(["name"], Sort.ASCENDING)\
        .limit(segment_length)\
        .offset(index*segment_length)\
        .execute(fetch_type=FetchType.FETCH_ALL, dictionary=True)

    difam_project_list = []
    for res in rs:
        difam_project_list.append(models.DifamProject(**res))

    return difam_project_list

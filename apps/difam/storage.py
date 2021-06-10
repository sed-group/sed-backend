from typing import List

from mysql.connector.pooling import PooledMySQLConnection

import apps.difam.models as models
from apps.core.projects.storage import db_get_user_subprojects_with_application_sid
from libs.mysqlutils import MySQLStatementBuilder, FetchType, Sort

DIFAM_APPLICATION_SID = "MOD.DIFAM"
DIFAM_TABLE = "difam_projects"
DIFAM_COLUMNS = ["id", "name", "individual_archetype_id", "owner_id", "datetime_created"]


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

from typing import List

from mysql.connector.pooling import PooledMySQLConnection

import apps.difam.models as models
import apps.difam.exceptions as exceptions
import apps.core.authentication.exceptions as authorization_exceptions
from apps.core.exceptions import NoChangeException
from apps.core.users.storage import db_get_user_safe_with_id
from apps.core.projects.storage import db_get_user_subprojects_with_application_sid
from apps.core.individuals.storage import db_get_individual
from apps.core.individuals.exceptions import IndividualNotFoundException
from libs.mysqlutils import MySQLStatementBuilder, FetchType, Sort
from libs.datastructures.pagination import ListChunk

DIFAM_APPLICATION_SID = "MOD.DIFAM"
DIFAM_TABLE = "difam_projects"
DIFAM_COLUMNS = ["id", "name", "individual_archetype_id", "owner_id", "datetime_created"]


def db_delete_project(con: PooledMySQLConnection, difam_project_id: int, current_user_id: int) -> bool:
    select_stmnt = MySQLStatementBuilder(con)
    res = select_stmnt\
        .select(DIFAM_TABLE, ['owner_id'])\
        .where('id = %s', [difam_project_id])\
        .execute(fetch_type=FetchType.FETCH_ONE, dictionary=True)

    if res is None:
        raise exceptions.DifamProjectNotFoundException

    if res["owner_id"] != current_user_id:
        raise authorization_exceptions.UnauthorizedOperationException

    delete_stmnt = MySQLStatementBuilder(con)
    res, rows = delete_stmnt.delete(DIFAM_TABLE)\
        .where("id = %s", [difam_project_id])\
        .execute(return_affected_rows=True)

    if rows == 0:
        raise NoChangeException

    return True


def db_put_project_archetype(con, difam_project_id: int, individual_archetype_id: int) -> models.DifamProject:
    update_stmnt = MySQLStatementBuilder(con)

    # Assert that project exists
    db_get_difam_project(con, difam_project_id) # Raises if project does not exist

    # Assert that the archetype exists
    db_get_individual(con, individual_archetype_id, archetype=True)

    print(f"Set arch = {individual_archetype_id} where id = {difam_project_id}")
    res, rows = update_stmnt\
        .update(DIFAM_TABLE, "individual_archetype_id = %s", [individual_archetype_id])\
        .where("id = %s", [difam_project_id])\
        .execute(fetch_type=FetchType.FETCH_NONE, return_affected_rows=True)

    if rows == 0:
        return db_get_difam_project(con, difam_project_id)

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

    return populate_difam_project(con, res)


def db_get_difam_projects(con: PooledMySQLConnection, segment_length: int, index: int, current_user_id: int) \
        -> ListChunk[models.DifamProject]:
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
        difam_project_list.append(populate_difam_project(con, res)) # Resource consuming for large batches

    count_stmnt = MySQLStatementBuilder(con)
    res = count_stmnt.count(DIFAM_TABLE).where(where_stmnt, where_values).execute(fetch_type=FetchType.FETCH_ONE,
                                                                                  dictionary=True)
    chunk = ListChunk[models.DifamProject](chunk=difam_project_list, length_total=res["count"])

    return chunk


def db_post_generate_individuals (con, individual_archetype_id: int, range_parameters: List[models.RangeParameter],
                                  current_user_id: int):
    for range_parameter in range_parameters:
        print(range_parameter)


def populate_difam_project (con, difam_project_database_result):
    res = difam_project_database_result
    try:
        archetype = db_get_individual(con, res['individual_archetype_id'], archetype=True)
    except IndividualNotFoundException:
        archetype = None

    return models.DifamProject(
        id=res['id'],
        name=res['name'],
        owner=db_get_user_safe_with_id(con, res['owner_id']),
        archetype=archetype,
        datetime_created=res['datetime_created']
    )

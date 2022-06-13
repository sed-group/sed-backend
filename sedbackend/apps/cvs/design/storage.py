from typing import List

from fastapi.logger import logger
from mysql.connector.pooling import PooledMySQLConnection

from sedbackend.apps.cvs.vcs.storage import get_vcs, get_value_driver
from sedbackend.libs.datastructures.pagination import ListChunk
from sedbackend.libs.mysqlutils import MySQLStatementBuilder, FetchType, Sort
from sedbackend.apps.cvs.design import models, exceptions
from sedbackend.apps.cvs.vcs import models as vcs_models

DESIGNS_TABLE = 'cvs_designs'
DESIGNS_COLUMNS = ['id', 'project', 'vcs', 'name', 'description']

QUANTIFIED_OBJECTIVE_TABLE = 'cvs_quantified_objectives'
QUANTIFIED_OBJECTIVE_COLUMNS = ['id', 'design', 'value_driver', 'name', 'property', 'unit']


def create_design(db_connection: PooledMySQLConnection, design_post: models.DesignPost, vcs_id: int, project_id: int,
                  user_id: int) -> models.Design:
    logger.debug(f'creating design with vcs_id={vcs_id} and project_id={project_id}')
    get_vcs(db_connection, vcs_id, project_id, user_id)  # perform checks: project, vcs and user

    insert_statement = MySQLStatementBuilder(db_connection)
    insert_statement \
        .insert(table=DESIGNS_TABLE, columns=['project', 'vcs', 'name', 'description']) \
        .set_values([project_id, vcs_id, design_post.name, design_post.description]) \
        .execute(fetch_type=FetchType.FETCH_NONE)
    design_id = insert_statement.last_insert_id

    return get_design(db_connection, design_id, project_id, vcs_id, user_id)


def get_design(db_connection: PooledMySQLConnection, design_id: int, project_id: int, vcs_id: int,
               user_id: int) -> models.Design:
    select_statement = MySQLStatementBuilder(db_connection)

    get_vcs(db_connection, vcs_id, project_id, user_id)  # perform checks: project, vcs and user

    result = select_statement \
        .select(DESIGNS_TABLE, DESIGNS_COLUMNS) \
        .where('id = %s', [design_id]) \
        .execute(fetch_type=FetchType.FETCH_ONE, dictionary=True)

    if result is None:
        raise exceptions.DesignNotFoundException

    return populate_design(db_connection, result, project_id, vcs_id, user_id)


def get_all_designs(db_connection: PooledMySQLConnection, project_id: int, vcs_id: int,
                    user_id: int) -> ListChunk[models.Design]:
    logger.debug(f'Fetching all Designs with project_id={project_id}, vcs_id={vcs_id}')

    get_vcs(db_connection, vcs_id, project_id, user_id)  # perform checks: project, vcs and user

    select_statement = MySQLStatementBuilder(db_connection)
    results = select_statement \
        .select(DESIGNS_TABLE, DESIGNS_COLUMNS) \
        .where('vcs = %s and project = %s', [vcs_id, project_id]) \
        .order_by(['id'], Sort.ASCENDING) \
        .execute(fetch_type=FetchType.FETCH_ALL, dictionary=True)

    logger.debug(results)

    design_list = []
    for result in results:
        design_list.append(populate_design(db_connection, result, project_id, vcs_id, user_id))

    count_statement = MySQLStatementBuilder(db_connection)
    result = count_statement.count(DESIGNS_TABLE) \
        .where('vcs = %s', [vcs_id]) \
        .execute(fetch_type=FetchType.FETCH_ONE, dictionary=True)
    chunk = ListChunk[models.Design](chunk=design_list, length_total=result['count'])
    return chunk


def delete_design(db_connection: PooledMySQLConnection, design_id: int, project_id: int, vcs_id: int,
                  user_id: int) -> bool:
    logger.debug(f'Deleting design with id={design_id}')

    get_vcs(db_connection, vcs_id, project_id, user_id)  # perform checks: project, vcs and user

    select_statement = MySQLStatementBuilder(db_connection)
    result = select_statement \
        .select(DESIGNS_TABLE, DESIGNS_COLUMNS) \
        .where('id = %s', [design_id]) \
        .execute(fetch_type=FetchType.FETCH_ONE, dictionary=True)

    if result is None:
        raise exceptions.DesignNotFoundException

    if delete_all_quantified_objectives(db_connection, design_id):
        pass
    else:
        raise exceptions.QuantifiedObjectivesNotDeleted

    delete_statement = MySQLStatementBuilder(db_connection)
    _, rows = delete_statement.delete(DESIGNS_TABLE) \
        .where('id = %s', [design_id]) \
        .execute(return_affected_rows=True)

    if rows == 0:
        raise exceptions.DesignNotFoundException

    return True


def edit_design(db_connection: PooledMySQLConnection, design_id: int, project_id: int, vcs_id: int, user_id: int,
                updated_design: models.DesignPost) -> models.Design:
    logger.debug(f'Editing Design with id = {design_id}')

    get_vcs(db_connection, vcs_id, project_id, user_id)  # perform checks: project, vcs and user

    update_statement = MySQLStatementBuilder(db_connection)
    update_statement.update(
        table=DESIGNS_TABLE,
        set_statement='name = %s, description = %s',
        values=[updated_design.name, updated_design.description]
    )
    update_statement.where('id = %s', [design_id])
    _, rows = update_statement.execute(return_affected_rows=True)

    if rows == 0:
        raise exceptions.DesignNotFoundException

    return get_design(db_connection, design_id, project_id, vcs_id, user_id)


def populate_design(db_connection: PooledMySQLConnection, db_result, project_id: int, vcs_id: int,
                    user_id: int) -> models.Design:
    return models.Design(
        id=db_result['id'],
        vcs=get_vcs(db_connection, vcs_id=vcs_id, project_id=project_id, user_id=user_id),
        name=db_result['name'],
        description=db_result['description']
    )


def get_quantified_objective(db_connection: PooledMySQLConnection, quantified_objective_id: int,
                             design_id: int, value_driver_id: int, project_id: int, vcs_id: int,
                             user_id: int) -> models.QuantifiedObjective:
    logger.debug(f'Get quantified objective with id = {design_id}')

    get_design(db_connection, design_id, project_id, vcs_id, user_id)  # perform checks
    get_value_driver(db_connection, value_driver_id, project_id, user_id)

    select_statement = MySQLStatementBuilder(db_connection)
    result = select_statement \
        .select(QUANTIFIED_OBJECTIVE_TABLE, QUANTIFIED_OBJECTIVE_COLUMNS) \
        .where('id = %s', [quantified_objective_id]) \
        .execute(fetch_type=FetchType.FETCH_ONE, dictionary=True)

    if result is None:
        raise exceptions.QuantifiedObjectiveNotFoundException

    return populate_QO(db_connection, result, design_id, value_driver_id, project_id, user_id)


def get_all_quantified_objectives(db_connection: PooledMySQLConnection, design_id: int,
                                  project_id: int, vcs_id: int, user_id: int) -> List[
    models.QuantifiedObjective]:
    logger.debug(f'Get all quantified objectives for design with id = {design_id}')

    get_design(db_connection, design_id, project_id, vcs_id, user_id)  # perform checks

    select_statement = MySQLStatementBuilder(db_connection)
    res = select_statement \
        .select(QUANTIFIED_OBJECTIVE_TABLE, QUANTIFIED_OBJECTIVE_COLUMNS) \
        .where('design = %s', [design_id]) \
        .execute(fetch_type=FetchType.FETCH_ALL, dictionary=True)

    if res is None:
        raise exceptions.QuantifiedObjectiveNotFoundException

    qo_list = []

    for result in res:
        qo_list.append(populate_QO(db_connection, result, design_id, result['value_driver'], project_id, user_id))

    return qo_list


def create_quantified_objective(db_connection: PooledMySQLConnection, design_id: int, value_driver_id: int,
                                quantified_objective_post: models.QuantifiedObjectivePost, project_id: int, vcs_id: int,
                                user_id: int) -> models.QuantifiedObjective:
    logger.debug(f'Create quantified objective for design with id = {design_id}')

    get_design(db_connection, design_id, project_id, vcs_id, user_id)
    get_value_driver(db_connection, value_driver_id, project_id, user_id)

    insert_statement = MySQLStatementBuilder(db_connection)
    insert_statement \
        .insert(table=QUANTIFIED_OBJECTIVE_TABLE, columns=['design', 'value_driver', 'name', 'property', 'unit']) \
        .set_values([design_id, value_driver_id, quantified_objective_post.name, quantified_objective_post.property,
                     quantified_objective_post.unit]) \
        .execute(fetch_type=FetchType.FETCH_NONE)
    quantified_id = insert_statement.last_insert_id

    return get_quantified_objective(db_connection, quantified_id, design_id, value_driver_id, project_id, vcs_id, user_id)


def delete_quantified_objective(db_connection: PooledMySQLConnection, quantified_objective_id: int,
                                value_driver_id: int, design_id: int, project_id: int, vcs_id: int,
                                user_id: int) -> bool:
    logger.debug(f'Delete quantified objectives with id = {quantified_objective_id}')

    get_design(db_connection, design_id, project_id, vcs_id, user_id)  # perform checks
    get_value_driver(db_connection, value_driver_id, project_id, user_id)

    select_statement = MySQLStatementBuilder(db_connection)
    result = select_statement \
        .select(QUANTIFIED_OBJECTIVE_TABLE, QUANTIFIED_OBJECTIVE_COLUMNS) \
        .where('id = %s', [quantified_objective_id]) \
        .execute(fetch_type=FetchType.FETCH_ONE, dictionary=True)

    if result is None:
        raise exceptions.QuantifiedObjectiveNotFoundException

    delete_statement = MySQLStatementBuilder(db_connection)
    _, rows = delete_statement.delete(QUANTIFIED_OBJECTIVE_TABLE) \
        .where('id = %s', [quantified_objective_id]) \
        .execute(return_affected_rows=True)

    if rows == 0:
        raise exceptions.QuantifiedObjectiveNotFoundException

    return True


# Do not open up for api. Should only be used when deleting other table entries.
def delete_all_quantified_objectives(db_connection: PooledMySQLConnection, design_id: int) -> bool:
    logger.debug(f'Deleting all quantified objectives with design id = {design_id}')

    delete_statement = MySQLStatementBuilder(db_connection)
    _, rows = delete_statement.delete(QUANTIFIED_OBJECTIVE_TABLE) \
        .where('design = %s', [design_id]) \
        .execute(return_affected_rows=True)

    return True


def edit_quantified_objective(db_connection: PooledMySQLConnection, quantified_objective_id: int, design_id: int,
                              value_driver_id: int, updated_qo: models.QuantifiedObjectivePost, user_id: int,
                              project_id: int, vcs_id: int) -> models.QuantifiedObjective:
    logger.debug(f'Editing quantified objective with id = {quantified_objective_id}')

    get_design(db_connection, design_id, project_id, vcs_id, user_id)
    get_value_driver(db_connection, value_driver_id, project_id, user_id)

    update_statement = MySQLStatementBuilder(db_connection)
    update_statement.update(
        table=QUANTIFIED_OBJECTIVE_TABLE,
        set_statement='name = %s, property = %s, unit = %s',
        values=[updated_qo.name, updated_qo.property, updated_qo.unit]
    )
    update_statement.where('id = %s', [quantified_objective_id])
    _, rows = update_statement.execute(return_affected_rows=True)

    if rows == 0:
        raise exceptions.QuantifiedObjectiveNotFoundException

    return (get_quantified_objective(db_connection, quantified_objective_id, design_id, value_driver_id, project_id,
                                     vcs_id, user_id))


def populate_QO(db_connection: PooledMySQLConnection, db_result,
                design_id: int, value_driver_id: int, project_id: int, user_id: int) -> models.QuantifiedObjective:
    return models.QuantifiedObjective(
        id=db_result['id'],
        design=design_id,
        value_driver=get_value_driver(db_connection, value_driver_id, project_id, user_id),
        name=db_result['name'],
        property=db_result['property'],
        unit=db_result['unit'],
        processes=get_table_rows_from_driver(db_connection, value_driver_id, project_id, user_id)
    )

'''
# TODO change the way that stakeholder needs and value drivers are stored.
def get_table_rows_from_driver(db_connection: PooledMySQLConnection, value_driver_id: int,
                               project_id: int, user_id: int) -> List[vcs_models.TableRowGet]:
    select_statement = MySQLStatementBuilder(db_connection)
    stakeholder_need_ids = select_statement \
        .select(CVS_VCS_NEEDS_DRIVERS_MAP_TABLE, ['stakeholder_need_id']) \
        .where('value_driver_id = %s', [value_driver_id]) \
        .execute(fetch_type=FetchType.FETCH_ALL, dictionary=True)

    table_rows = []
    for need_id in stakeholder_need_ids:
        select_statement = MySQLStatementBuilder(db_connection)
        table_row_ids = select_statement \
            .select(CVS_VCS_STAKEHOLDER_NEED_TABLE, ['table_row_id']) \
            .where('id = %s', [need_id['stakeholder_need_id']]) \
            .execute(fetch_type=FetchType.FETCH_ALL, dictionary=True)

        for table_row_id in table_row_ids:
            select_statement = MySQLStatementBuilder(db_connection)
            result = select_statement \
                .select(CVS_VCS_TABLE_ROWS_TABLE, CVS_VCS_TABLE_ROWS_COLUMNS) \
                .where('id = %s', [table_row_id['table_row_id']]) \
                .execute(fetch_type=FetchType.FETCH_ONE, dictionary=True)

            table_rows.append(populate_table_row(db_connection, result, project_id, user_id))

    return table_rows
'''
from typing import Union, Optional, List, Dict

from mysql.connector.pooling import PooledMySQLConnection
from fastapi.logger import  logger

import sedbackend.apps.core.individuals.models as models
import sedbackend.apps.core.individuals.exceptions as ex
from sedbackend.libs.mysqlutils import MySQLStatementBuilder, FetchType, exclude_cols

INDIVIDUALS_TABLE = 'individuals'
INDIVIDUALS_COLUMNS = ['id', 'name', 'is_archetype']
INDIVIDUALS_PARAMETERS_TABLE = 'individuals_parameters'
INDIVIDUALS_PARAMETERS_COLUMNS = ['id', 'name', 'value', 'type', 'individual_id']
INDIVIDUALS_ARCHETYPES_MAP_TABLE = 'individuals_archetypes_map'
INDIVIDUALS_ARCHETYPES_MAP_COLUMNS = ['id', 'individual_archetype_id', 'individual_id']


def db_assert_individual_exists(con: PooledMySQLConnection, individual_id: int) -> bool:
    select_stmnt = MySQLStatementBuilder(con)
    res = select_stmnt.select(INDIVIDUALS_TABLE, ['id'])\
        .where("id = %s", [individual_id])\
        .execute(fetch_type=FetchType.FETCH_ONE, dictionary=True)

    if res is not None:
        return True

    return False


def db_get_individual(con: PooledMySQLConnection, individual_id: int, archetype: bool = False) \
        -> Optional[Union[models.Individual, models.IndividualArchetype]]:

    where_stmnt = "id = %s"
    if archetype is True:
        where_stmnt += " AND is_archetype = 1"
    else:
        where_stmnt += " AND is_archetype = 0"

    select_stmnt = MySQLStatementBuilder(con)
    res = select_stmnt\
        .select(INDIVIDUALS_TABLE, INDIVIDUALS_COLUMNS)\
        .where(where_stmnt, [individual_id])\
        .execute(fetch_type=FetchType.FETCH_ONE, dictionary=True)

    if res is None:
        raise ex.IndividualNotFoundException(f'No individual or individual archetype found '
                                             f'with id {individual_id} with archetype set to {archetype}')

    individual = parse_individual_from_db(con, res, archetype)

    return individual


def db_post_individual_archetype(con: PooledMySQLConnection, individual_archetype: models.IndividualArchetypePost):
    return db_post_individual(con, individual_archetype, is_archetype=True)


def db_post_individual(connection, individual: Union[models.IndividualArchetypePost, models.IndividualPost],
                       is_archetype: bool = False) -> Union[models.IndividualArchetype, models.Individual]:
    insert_stmnt = MySQLStatementBuilder(connection)

    if is_archetype is False:
        insert_stmnt\
            .insert(INDIVIDUALS_TABLE, ["name"])\
            .set_values([individual.name])\
            .execute()
    else:
        insert_stmnt\
            .insert(INDIVIDUALS_TABLE, ["name", "is_archetype"])\
            .set_values([individual.name, 1])\
            .execute()

    individual_id = insert_stmnt.last_insert_id

    if len(individual.parameters) == 0:
        return db_get_individual(connection, individual_id, archetype=is_archetype)

    for parameter in individual.parameters:
        pvalue_unparsed = parameter.value
        if parameter.type is None:
            ptype = models.ParameterType.get_parameter_type(pvalue_unparsed).value
        else:
            ptype = parameter.type

        pvalue = str(pvalue_unparsed)

        insert_param_stmnt = MySQLStatementBuilder(connection)
        insert_param_stmnt\
            .insert(INDIVIDUALS_PARAMETERS_TABLE, exclude_cols(INDIVIDUALS_PARAMETERS_COLUMNS, ['id']))\
            .set_values([parameter.name, pvalue, ptype, individual_id])\
            .execute()

    if type(individual) is models.IndividualPost and individual.archetype_id is not None:
        insert_archetype_mapping_stmnt = MySQLStatementBuilder(connection)
        insert_archetype_mapping_stmnt\
            .insert(INDIVIDUALS_ARCHETYPES_MAP_TABLE, ['individual_archetype_id', 'individual_id'])\
            .set_values([individual.archetype_id, individual_id])\
            .execute()

    return db_get_individual(connection, individual_id, archetype=is_archetype)


def db_put_individual_name(con, individual_id, individual_name, archetype=False) \
        -> Union[models.Individual, models.IndividualArchetype]:

    # Assert that individual exists
    individual = db_get_individual(con, individual_id, archetype=archetype)

    update_stmnt = MySQLStatementBuilder(con)
    res, rows = update_stmnt\
        .update(INDIVIDUALS_TABLE, "name = %s", [individual_name])\
        .where("id = %s", [individual_id])\
        .execute(return_affected_rows=True)

    if rows == 0:
        return individual

    return db_get_individual(con, individual_id, archetype=archetype)


def db_get_archetype_id_of_individual(con, individual_id):
    select_stmnt = MySQLStatementBuilder(con)
    res = select_stmnt\
        .select(INDIVIDUALS_ARCHETYPES_MAP_TABLE, ["individual_archetype_id"])\
        .where("individual_id = %s", [individual_id])\
        .execute(fetch_type=FetchType.FETCH_ONE, dictionary=True)

    if res is None:
        return None

    return res["individual_archetype_id"]


def db_get_parameter(con, parameter_id, individual_id) -> models.IndividualParameter:
    select_stmnt = MySQLStatementBuilder(con)
    res = select_stmnt\
        .select(INDIVIDUALS_PARAMETERS_TABLE, INDIVIDUALS_PARAMETERS_COLUMNS)\
        .where("id = %s AND individual_id = %s", [parameter_id, individual_id])\
        .execute(fetch_type=FetchType.FETCH_ONE, dictionary=True)

    if res is None:
        raise ex.ParameterNotFoundException

    parameter = models.IndividualParameter(**res)
    parameter.value = parameter.get_parsed_value()
    return parameter


def db_get_parameters(con: PooledMySQLConnection, parameter_id_list: List[int]) -> Dict[int, models.IndividualParameter]:
    select_stmnt = MySQLStatementBuilder(con)
    rs = select_stmnt\
        .select(INDIVIDUALS_PARAMETERS_TABLE, INDIVIDUALS_PARAMETERS_COLUMNS)\
        .where("id IN " + MySQLStatementBuilder.placeholder_array(len(parameter_id_list)), parameter_id_list)\
        .execute(fetch_type=FetchType.FETCH_ALL, dictionary=True)

    if rs is None:
        raise ex.ParameterNotFoundException

    parameters_dict = {}
    for res in rs:
        parameter = models.IndividualParameter(**res)
        parameter.value = parameter.get_parsed_value()
        parameters_dict[parameter.id] = parameter

    if len(parameters_dict) == 0:
        raise ex.ParameterNotFoundException

    return parameters_dict


def db_get_parameter_with_name(con: PooledMySQLConnection, individual_id, name) -> models.IndividualParameter:
    select_stmnt = MySQLStatementBuilder(con)
    logger.debug(f'Get parameter with name = "{name}"')

    res = select_stmnt\
        .select(INDIVIDUALS_PARAMETERS_TABLE, INDIVIDUALS_PARAMETERS_COLUMNS)\
        .where(f"individual_id = %s AND name = %s", [individual_id, name])\
        .execute(fetch_type=FetchType.FETCH_ONE, dictionary=True)

    if res is None:
        logger.debug(f'Failed to find parameter with name = {name}')
        raise ex.ParameterNotFoundException

    logger.debug(f'Found parameter with name = {name}')
    parameter = models.IndividualParameter(**res)
    parameter.value = parameter.get_parsed_value()
    return parameter


def db_post_parameter(con, individual_id: int, parameter: models.IndividualParameterPost) -> models.IndividualParameter:
    logger.debug(f'Post parameter with name "{parameter.name}" to individual with id = {individual_id}')

    # Set parameter type
    if parameter.type is None:
        ptype = models.ParameterType.get_parameter_type(parameter.value).value
    else:
        ptype = parameter.type

    # Assert that the individual exists
    individual_exists = db_assert_individual_exists(con, individual_id)
    if individual_exists is False:
        logger.debug("Individual exists")
        raise ex.IndividualNotFoundException

    # Assert that no other parameter for specified individual has the same name
    try:
        logger.debug("Ensure that the parameter is not a duplicate..")
        p_duplicate = db_get_parameter_with_name(con, individual_id, parameter.name)
        if p_duplicate is not None:
            logger.debug("Parameter was a duplicate. Raising.")
            raise ex.DuplicateParameterException
    except ex.ParameterNotFoundException:
        logger.debug("Parameter was not a duplicate. Moving on..")
        pass

    insert_stmnt = MySQLStatementBuilder(con)
    insert_stmnt\
        .insert(INDIVIDUALS_PARAMETERS_TABLE, ['name', 'value', 'type', 'individual_id'])\
        .set_values([parameter.name, str(parameter.value), ptype, individual_id])\
        .execute()

    parameter_id = insert_stmnt.last_insert_id

    return db_get_parameter(con, parameter_id, individual_id)


def db_delete_parameter(con, individual_id: int, parameter_id: int) -> bool:
    delete_stmnt = MySQLStatementBuilder(con)
    res, rows = delete_stmnt\
        .delete(INDIVIDUALS_PARAMETERS_TABLE)\
        .where("individual_id = %s AND id = %s", [individual_id, parameter_id])\
        .execute(return_affected_rows=True)

    if rows == 0:
        raise ex.ParameterNotFoundException

    return True


def db_get_archetype_individuals(con: PooledMySQLConnection, archetype_id: int) -> List[models.Individual]:
    # Assert that the archetype exists
    db_get_individual(con, archetype_id, archetype=True)

    nested_stmnt = "(SELECT individual_id FROM individuals_archetypes_map WHERE individual_archetype_id = %s)"
    select_stmnt = MySQLStatementBuilder(con)
    rs = select_stmnt\
        .select(INDIVIDUALS_TABLE, INDIVIDUALS_COLUMNS)\
        .where(f"id IN ({nested_stmnt})", [archetype_id])\
        .execute(fetch_type=FetchType.FETCH_ALL, dictionary=True)

    individuals = []
    for res in rs:
        individuals.append(parse_individual_from_db(con, res, archetype=False, archetype_id=archetype_id))

    return individuals


def db_get_archetype_individuals_count(con: PooledMySQLConnection, archetype_id: int) -> int:
    # Assert that the archetype exists
    db_get_individual(con, archetype_id, archetype=True)

    nested_stmnt = "(SELECT individual_id FROM individuals_archetypes_map WHERE individual_archetype_id = %s)"
    select_stmnt = MySQLStatementBuilder(con)
    res = select_stmnt\
        .count(INDIVIDUALS_TABLE)\
        .where(f"id IN ({nested_stmnt})", [archetype_id])\
        .execute(dictionary=True)
    return res['count']


def db_delete_archetype_individuals(con: PooledMySQLConnection, archetype_id: int) -> int:
    nested_stmnt = "(SELECT individual_id FROM individuals_archetypes_map WHERE individual_archetype_id = %s)"
    delete_stmnt = MySQLStatementBuilder(con)
    res, rows = delete_stmnt\
        .delete(INDIVIDUALS_TABLE)\
        .where(f"id IN ({nested_stmnt})", [archetype_id])\
        .execute(return_affected_rows=True)

    return rows


def db_delete_individual(con: PooledMySQLConnection, individual_id) -> bool:
    delete_stmnt = MySQLStatementBuilder(con)
    res, rows = delete_stmnt\
        .delete(INDIVIDUALS_TABLE)\
        .where("id = %s", [individual_id])\
        .execute(return_affected_rows=True)

    if rows == 0:
        raise ex.IndividualNotFoundException

    return True


def parse_individual_from_db(con: PooledMySQLConnection, db_res,
                             archetype: Optional[bool] = False,
                             archetype_id: Optional[int] = None):
    """
    Construct individual using database row
    :param con:
    :param db_res:
    :param archetype:
    :param archetype_id:
    :return:
    """
    if archetype:
        individual = models.IndividualArchetype(id=db_res['id'], name=db_res['name'])
    else:
        individual = models.Individual(id=db_res['id'], name=db_res['name'])

    # Set parameters
    select_parameters_stmnt = MySQLStatementBuilder(con)
    rs = select_parameters_stmnt\
        .select(INDIVIDUALS_PARAMETERS_TABLE, INDIVIDUALS_PARAMETERS_COLUMNS)\
        .where("individual_id = %s", [individual.id])\
        .execute(fetch_type=FetchType.FETCH_ALL, dictionary=True)

    for res in rs:
        param = models.IndividualParameter(**res)
        param.value = param.get_parsed_value()  # Value is stored as string in DB. Convert to correct format.
        individual.parameters.append(param)

    # Set archetype id (if not an archetype itself)
    if archetype is False:
        if archetype_id is None:
            individual.archetype_id = db_get_archetype_id_of_individual(con, individual.id)
        else:
            individual.archetype_id = archetype_id

    return individual

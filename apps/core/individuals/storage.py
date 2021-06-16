from typing import Union, Optional, Any

from mysql.connector.pooling import PooledMySQLConnection

import apps.core.individuals.models as models
import apps.core.individuals.exceptions as ex
from libs.mysqlutils import MySQLStatementBuilder, FetchType, exclude_cols

INDIVIDUALS_TABLE = 'individuals'
INDIVIDUALS_COLUMNS = ['id', 'name', 'is_archetype']
INDIVIDUALS_PARAMETERS_TABLE = 'individuals_parameters'
INDIVIDUALS_PARAMETERS_COLUMNS = ['id', 'name', 'value', 'type', 'individual_id']
INDIVIDUALS_ARCHETYPES_MAP_TABLE = 'individuals_archetypes_map'
INDIVIDUALS_ARCHETYPES_MAP_COLUMNS = ['id', 'individual_archetype_id', 'individual_id']


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

    if archetype:
        individual = models.IndividualArchetype(id=res['id'], name=res['name'])
    else:
        individual = models.Individual(id=res['id'], name=res['name'])

    # Set parameters
    select_parameters_stmnt = MySQLStatementBuilder(con)
    rs = select_parameters_stmnt\
        .select(INDIVIDUALS_PARAMETERS_TABLE, INDIVIDUALS_PARAMETERS_COLUMNS)\
        .where("individual_id = %s", [individual_id])\
        .execute(fetch_type=FetchType.FETCH_ALL, dictionary=True)

    for res in rs:
        print(res)
        param = models.IndividualParameter(**res)
        individual.parameters[param.name] = param.get_parsed_value()

    # Set archetype id (if not an archetype iteself)
    if archetype is False:
        individual.archetype_id = db_get_archetype_id_of_individual(con, individual_id)

    return individual


def db_post_individual_archetype(con: PooledMySQLConnection, individual_archetype: models.IndividualArchetypePost):
    return db_post_individual(con, individual_archetype, is_archetype=True)


def db_post_individual(connection, individual: Union[models.IndividualArchetypePost, models.IndividualPost],
                       is_archetype: bool = False):
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

    if len(individual.parameters.keys()) == 0:
        return db_get_individual(connection, individual_id, archetype=is_archetype)

    for pname in individual.parameters.keys():
        pvalue_unparsed = individual.parameters[pname]
        ptype = models.ParameterType.get_parameter_type(pvalue_unparsed).value
        pvalue = str(pvalue_unparsed)

        insert_param_stmnt = MySQLStatementBuilder(connection)
        insert_param_stmnt\
            .insert(INDIVIDUALS_PARAMETERS_TABLE, exclude_cols(INDIVIDUALS_PARAMETERS_COLUMNS, ['id']))\
            .set_values([pname, pvalue, ptype, individual_id])\
            .execute()

    if type(individual) is models.IndividualPost and individual.archetype_id is not None:
        insert_archetype_mapping_stmnt = MySQLStatementBuilder(connection)
        insert_archetype_mapping_stmnt\
            .insert(INDIVIDUALS_ARCHETYPES_MAP_TABLE, ['individual_archetype_id', 'individual_id'])\
            .set_values([individual.archetype_id, individual_id])\
            .execute()

    return db_get_individual(connection, individual_id, archetype=is_archetype)


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

    return models.IndividualParameter(**res)


def db_post_parameter(con, individual_id: int, parameter: models.IndividualParameterPost):
    ptype = models.ParameterType.get_parameter_type(parameter.value).value

    insert_stmnt = MySQLStatementBuilder(con)
    insert_stmnt\
        .insert(INDIVIDUALS_PARAMETERS_TABLE, ['name', 'value', 'type', 'individual_id'])\
        .set_values([parameter.name, str(parameter.value), ptype, individual_id])\
        .execute()

    parameter_id = insert_stmnt.last_insert_id

    return db_get_parameter(con, parameter_id, individual_id)


def db_delete_parameter(con, individual_id: int, parameter_name: str):
    delete_stmnt = MySQLStatementBuilder(con)
    res, rows = delete_stmnt\
        .delete(INDIVIDUALS_PARAMETERS_TABLE)\
        .where("individual_id = %s AND name = %s", [individual_id, parameter_name])\
        .execute(return_affected_rows=True)

    if rows == 0:
        raise ex.ParameterNotFoundException(f'No parameter with the name "{parameter_name}" '
                                            f'found for individual with id = {individual_id}')

    return True

from apps.core.individuals.models import Individual, ParameterType, IndividualPost
from libs.mysqlutils import MySQLStatementBuilder, FetchType, exclude_cols

INDIVIDUALS_TABLE = 'individuals'
INDIVIDUALS_COLUMNS = ['id', 'name']
INDIVIDUALS_PARAMETERS_TABLE = 'individuals_parameters'
INDIVIDUALS_PARAMETERS_COLUMNS = ['id', 'name', 'value', 'type', 'individual_id']


def db_post_individual(connection, individual: IndividualPost):
    insert_stmnt = MySQLStatementBuilder(connection)
    insert_stmnt\
        .insert(INDIVIDUALS_TABLE, ["name"])\
        .set_values([individual.name])\
        .execute()

    individual_id = insert_stmnt.last_insert_id

    if len(individual.parameters.keys()) == 0:
        return

    for pname in individual.parameters.keys():
        pvalue_unparsed = individual.parameters[pname]
        ptype = ParameterType.get_parameter_type(pvalue_unparsed).value
        pvalue = str(pvalue_unparsed)

        insert_param_stmnt = MySQLStatementBuilder(connection)
        insert_param_stmnt\
            .insert(INDIVIDUALS_PARAMETERS_TABLE, exclude_cols(INDIVIDUALS_PARAMETERS_COLUMNS, ['id']))\
            .set_values([pname, pvalue, ptype, individual_id])\
            .execute()



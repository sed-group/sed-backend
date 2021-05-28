from apps.core.concepts.models import Concept, ParameterType, ConceptPost
from libs.mysqlutils import MySQLStatementBuilder, FetchType, exclude_cols

CONCEPTS_TABLE = 'concepts'
CONCEPTS_COLUMNS = ['id', 'name']
CONCEPTS_PARAMETERS_TABLE = 'concepts_parameters'
CONCEPTS_PARAMETERS_COLUMNS = ['id', 'name', 'value', 'type', 'concept_id']


def db_post_concept(connection, concept: ConceptPost):
    insert_stmnt = MySQLStatementBuilder(connection)
    insert_stmnt\
        .insert(CONCEPTS_TABLE, ["name"])\
        .set_values([concept.name])\
        .execute()

    concept_id = insert_stmnt.last_insert_id

    if len(concept.parameters.keys()) == 0:
        return

    for pname in concept.parameters.keys():
        pvalue_unparsed = concept.parameters[pname]
        ptype = ParameterType.get_parameter_type(pvalue_unparsed).value
        pvalue = str(pvalue_unparsed)

        insert_param_stmnt = MySQLStatementBuilder(connection)
        insert_param_stmnt\
            .insert(CONCEPTS_PARAMETERS_TABLE, exclude_cols(CONCEPTS_PARAMETERS_COLUMNS, ['id']))\
            .set_values([pname, pvalue, ptype, concept_id])\
            .execute()



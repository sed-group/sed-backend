
from apps.core.db import get_connection
from apps.core.individuals.storage import *
from apps.core.individuals.models import IndividualPost


def impl_post_individual(individual: IndividualPost):
    with get_connection() as con:
        res = db_post_individual(con, individual)
        con.commit()
        return res

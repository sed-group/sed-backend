
from apps.core.db import get_connection
from apps.core.concepts.storage import *
from apps.core.concepts.models import ConceptPost


def impl_post_concept(concept: ConceptPost):
    with get_connection() as con:
        db_post_concept(con, concept)
        con.commit()

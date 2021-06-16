from typing import Optional, Any

from fastapi import HTTPException, status

from apps.core.db import get_connection
import apps.core.individuals.storage as storage
import apps.core.individuals.models as models
import apps.core.individuals.exceptions as ex


def impl_get_individual(individual_id) -> Optional[models.Individual]:
    try:
        with get_connection() as con:
            return storage.db_get_individual(con, individual_id, archetype=False)
    except ex.IndividualNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Individual with id {individual_id} could not be found."
        )


def impl_get_individual_archetype(individual_archetype_id) -> Optional[models.IndividualArchetype]:
    try:
        with get_connection() as con:
            return storage.db_get_individual(con, individual_archetype_id, archetype=True)
    except ex.IndividualNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Individual with id {individual_archetype_id} could not be found."
        )


def impl_post_individual(individual: models.IndividualPost):
    with get_connection() as con:
        res = storage.db_post_individual(con, individual)
        con.commit()
        return res


def impl_post_individual_archetype(individual_archetype: models.IndividualArchetypePost):
    with get_connection() as con:
        res = storage.db_post_individual_archetype(con, individual_archetype)
        con.commit()
        return res


def impl_post_parameter(individual_id: int, parameter: models.IndividualParameterPost):
    with get_connection() as con:
        res = storage.db_post_parameter(con, individual_id, parameter)
        con.commit()
        return res


def impl_delete_parameter(individual_id: int, parameter_name: str):
    try:
        with get_connection() as con:
            res = storage.db_delete_parameter(con, individual_id, parameter_name)
            con.commit()
            return res
    except ex.ParameterNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Could not delete parameter "{parameter_name}". '
                   f'No parameter with that name for individual with id = {individual_id}'
        )

from typing import Optional, Union, List

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


def impl_post_individual(individual: models.IndividualPost) -> models.Individual:
    with get_connection() as con:
        res = storage.db_post_individual(con, individual)
        con.commit()
        return res


def impl_post_individual_archetype(individual_archetype: models.IndividualArchetypePost) -> models.IndividualArchetype:
    with get_connection() as con:
        res = storage.db_post_individual_archetype(con, individual_archetype)
        con.commit()
        return res


def impl_put_individual_name(individual_id: int, individual_name: str, archetype: bool = False):
    try:
        with get_connection() as con:
            res = storage.db_put_individual_name(con, individual_id, individual_name, archetype=archetype)
            con.commit()
            return res
    except ex.IndividualNotFoundException:
        HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"No individual with id = {individual_id}"
        )


def impl_post_parameter(individual_id: int, parameter: models.IndividualParameterPost) -> models.IndividualParameter:
    try:
        with get_connection() as con:
            res = storage.db_post_parameter(con, individual_id, parameter)
            con.commit()
            return res
    except ex.DuplicateParameterException:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f'Parameter with name "{parameter.name} already exists for individual with id = {individual_id}'
        )
    except ex.IndividualNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'No individual with id = {individual_id}'
        )


def impl_delete_parameter(individual_id: int, parameter_id: int) -> bool:
    try:
        with get_connection() as con:
            res = storage.db_delete_parameter(con, individual_id, parameter_id)
            con.commit()
            return res
    except ex.ParameterNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Could not delete parameter "{parameter_id}". '
                   f'No such parameter in individual with id = {individual_id}'
        )


def impl_get_archetype_individuals(archetype_id: int) -> List[models.Individual]:
    try:
        with get_connection() as con:
            return storage.db_get_archetype_individuals(con, archetype_id)
    except ex.IndividualNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"No archetype individual with ID = {archetype_id}"
        )


def impl_get_archetype_individuals_count(archetype_id: int) -> int:
    try:
        with get_connection() as con:
            return storage.db_get_archetype_individuals_count(con, archetype_id)
    except ex.IndividualNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"No archetype individual with ID = {archetype_id}"
        )


def impl_delete_archetype_individuals(archetype_id: int) -> int:
    try:
        with get_connection() as con:
            res = storage.db_delete_archetype_individuals(con, archetype_id)
            con.commit()
            return res
    except ex.IndividualNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"No archetype individual with ID = {archetype_id}"
        )


def impl_delete_individual(individual_id: int) -> bool:
    try:
        with get_connection() as con:
            res = storage.db_delete_individual(con, individual_id)
            con.commit()
            return res
    except ex.IndividualNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"No individual with ID = {individual_id}"
        )

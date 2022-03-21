from typing import Optional, List

from fastapi import APIRouter

import sedbackend.apps.core.individuals.models as models
import sedbackend.apps.core.individuals.implementation as impl

router = APIRouter()


@router.post("/",
             summary="Create individual",
             description="Create a new individual",
             response_model=models.Individual)
async def post_individual(individual: models.IndividualPost):
    return impl.impl_post_individual(individual)


@router.get("/{individual_id}",
            summary="Get individual",
            response_model=models.Individual)
async def get_individual(individual_id) -> models.Individual:
    return impl.impl_get_individual(individual_id)


@router.delete("/{individual_id}",
               response_model=bool,
               summary="Delete individual")
async def delete_individual(individual_id: int):
    return impl.impl_delete_individual(individual_id)


@router.put("/{individual_id}/name",
            summary="Set individual name",
            response_model=models.Individual)
async def put_individual_name(individual_id, individual_name):
    return impl.impl_put_individual_name(individual_id, individual_name, archetype=False)


@router.post("/{individual_id}/parameters/",
             summary="Add parameter to individual",
             response_model=models.IndividualParameter)
async def post_parameter(individual_id: int, parameter: models.IndividualParameterPost):
    return impl.impl_post_parameter(individual_id, parameter)


@router.delete("/{individual_id}/parameters/{parameter_id}",
               summary="Delete a parameter from an individual",
               response_model=bool)
async def delete_parameter(individual_id: int, parameter_id: int):
    return impl.impl_delete_parameter(individual_id, parameter_id)


@router.post("/archetypes/",
             summary="Create individual archetype",
             description="Create a new individual archetype",
             response_model=models.IndividualArchetype)
async def post_individual_archetype(individual_archetype: models.IndividualArchetypePost):
    return impl.impl_post_individual_archetype(individual_archetype)


@router.get("/archetypes/{individual_archetype_id}",
            summary="Get archetype individual",
            response_model=models.IndividualArchetype)
async def get_individual_archetype(individual_archetype_id) -> Optional[models.IndividualArchetype]:
    return impl.impl_get_individual_archetype(individual_archetype_id)


@router.get("/archetypes/{individual_archetype_id}/individuals/",
            summary="Get all individuals that uses this archetype",
            response_model=List[models.Individual])
async def get_archetype_individuals(individual_archetype_id: int):
    return impl.impl_get_archetype_individuals(individual_archetype_id)


@router.get("/archetypes/{individual_archetype_id}/individuals/count",
            summary="Count all individuals that uses this archetype",
            response_model=int)
async def get_archetype_individuals_count(individual_archetype_id: int):
    return impl.impl_get_archetype_individuals_count(individual_archetype_id)


@router.put("/archetypes/{individual_archetype_id}/name",
            summary="Set archetype name",
            response_model=models.IndividualArchetype)
async def put_individual_archetype_name(individual_archetype_id, individual_name):
    return impl.impl_put_individual_name(individual_archetype_id, individual_name, archetype=True)


@router.delete("/archetypes/{individual_archetype_id}/individuals/",
               response_model=int,
               summary="Delete all individuals for specific archetype")
async def delete_archetype_individuals(individual_archetype_id: int):
    return impl.impl_delete_archetype_individuals(individual_archetype_id)

from typing import Optional, Any

from fastapi import APIRouter, Security, Depends

import apps.core.individuals.models as models
import apps.core.individuals.implementation as impl

router = APIRouter()


@router.post("/",
             summary="Create individual",
             description="Create a new individual")
async def post_individual(individual: models.IndividualPost):
    return impl.impl_post_individual(individual)


@router.post("/archetypes/",
             summary="Create individual archetype",
             description="Create a new individual archetype")
async def post_individual_archetype(individual_archetype: models.IndividualArchetypePost):
    return impl.impl_post_individual_archetype(individual_archetype)


@router.get("/{individual_id}",
            summary="Get individual")
async def get_individual(individual_id) -> models.Individual:
    return impl.impl_get_individual(individual_id)


@router.get("/archetypes/{individual_archetype_id}",
            summary="Get individual")
async def get_individual_archetype(individual_archetype_id) -> Optional[models.IndividualArchetype]:
    return impl.impl_get_individual_archetype(individual_archetype_id)


@router.post("/{individual_id}/parameters/",
             summary="Add parameter to individual")
async def post_parameter(individual_id: int, parameter_name: str, parameter_value: Any):
    return impl.impl_post_parameter(individual_id, parameter_name, parameter_value)


@router.delete("/{individual_id}/parameters/{parameter_id}",
               summary="Delete a parameter from an individual")
async def delete_parameter(individual_id: int, parameter_name: str):
    return impl.impl_delete_parameter(individual_id, parameter_name)

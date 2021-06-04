from fastapi import APIRouter, Security, Depends

from apps.core.individuals.models import Individual, IndividualPost
from apps.core.individuals.implementation import impl_post_individual

router = APIRouter()


@router.post("/",
             summary="Create individual",
             description="Create a new individual")
async def post_individual(individual: IndividualPost):
    return impl_post_individual(individual)

from fastapi import APIRouter, Security, Depends

from apps.core.concepts.models import Concept, ConceptPost
from apps.core.concepts.implementation import impl_post_concept

router = APIRouter()


@router.post("/",
             summary="Create concept",
             description="Create a new concept")
async def post_concept(concept: ConceptPost):
    return impl_post_concept(concept)

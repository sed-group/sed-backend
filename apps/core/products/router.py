from typing import List, Dict

from fastapi import APIRouter, Security, Depends

from apps.core.authentication.utils import verify_token, get_current_active_user
from apps.core.products.implementation import *
from apps.core.products.models import DesignParameter

router = APIRouter()


@router.post("/",
             summary="Create product",
             description="Create a new empty project"
             )
async def post_product(name: str, design_parameters: Dict[str, DesignParameter]):
    return impl_create_product(name, design_parameters)

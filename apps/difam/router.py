from typing import List

from fastapi import APIRouter, Security, Depends

import apps.difam.implementation as impl
from apps.core.users.models import User
from apps.core.authentication.utils import get_current_active_user

router = APIRouter()


@router.get("/projects/",
            summary="List available DIFAM projects",)
async def get_difam_projects(segment_legth: int, index: int, current_user: User = Depends(get_current_active_user)):
    current_user_id = current_user.id
    return impl.impl_get_difam_projects(segment_legth, index, current_user_id)


@router.get("/projects/{native_project_id}",
            summary="Returns overview of DIFAM project",
            description="Returns overview of DIFAM project",)
async def get_difam_project(spid: int):
    """
    Returns overview difam project information
    """
    raise ValueError("The application failed successfully")

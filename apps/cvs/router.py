from typing import List

from fastapi import APIRouter, Security, Depends

import apps.difam.implementation as impl
import apps.difam.models as models
from libs.datastructures.pagination import ListChunk
from apps.core.users.models import User
from apps.core.authentication.utils import get_current_active_user
from apps.core.projects.dependencies import SubProjectAccessChecker
from apps.core.projects.models import AccessLevel

router = APIRouter()

DIFAM_APP_SID = 'MOD.CVS'


@router.get("/projects/", summary="Just testing")
async def get_cvs_projects(n: int) -> str:
    return f'{n}^2 = {n * n}'

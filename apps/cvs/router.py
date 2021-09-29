from typing import List

from fastapi import APIRouter, Security, Depends

import apps.cvs.algorithms as algorithms

router = APIRouter()

DIFAM_APP_SID = 'MOD.CVS'


@router.get("/projects/", summary="Just testing")
async def get_cvs_projects(n: int) -> str:
    return f'{n} * {n} = {algorithms.square_a_number(n)}'

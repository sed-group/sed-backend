from email.policy import HTTP
from typing import List

from fastapi import HTTPException
from starlette import status

from sedbackend.apps.core.authentication import exceptions as auth_ex
from sedbackend.apps.core.db import get_connection
from sedbackend.apps.cvs.link_design_lifecycle import models, storage
from sedbackend.apps.cvs.link_design_lifecycle.exceptions import FormulasNotFoundException, VCSNotFoundException, WrongTimeUnitException


def create_formulas(vcs_row_id: int, formulas: models.FormulaPost) -> bool:
    with get_connection() as con:
        try: 
            storage.create_formulas(con, vcs_row_id, formulas)
        except FormulasNotFoundException:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'Could not find formula'
            )
        except WrongTimeUnitException as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f'Wrong time unit. Given unit: {e.time_unit}'
            )

def get_all_formulas(vcs_id: int, design_group: int) -> List[models.FormulaRowGet]:
    with get_connection() as con:
        try:
            storage.get_all_formulas(con, vcs_id, design_group)
        except VCSNotFoundException:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f'Could not find VCS with id {vcs_id}'
            )
        except WrongTimeUnitException as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail=f'Wrong time unit. Given unit: {e.time_unit}'
            )

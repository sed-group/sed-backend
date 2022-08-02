from typing import List

from fastapi import HTTPException
from starlette import status

from sedbackend.apps.core.authentication import exceptions as auth_ex
from sedbackend.apps.core.db import get_connection
from sedbackend.apps.cvs.project import exceptions as proj_exceptions
from sedbackend.apps.cvs.market_input import models, storage, exceptions


def get_all_market_inputs(project_id: int) -> List[models.MarketInputGet]:
    try:
        with get_connection() as con:
            db_result = storage.get_all_market_input(con, project_id)
            con.commit()
            return db_result
    except auth_ex.UnauthorizedOperationException:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Unauthorized user.',
        )
    except proj_exceptions.CVSProjectNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Could not find project with id={project_id}.',
        )
    except exceptions.MarketInputNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Could not find market input',
        )

'''
def create_market_input(vcs_row_id: int, market_input: models.MarketInputPost) -> bool:
    try:
        with get_connection() as con:
            db_result = storage.create_market_input(con, vcs_row_id, market_input)
            con.commit()
            return db_result
    except auth_ex.UnauthorizedOperationException:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Unauthorized user.',
        )
    except vcs_exceptions.VCSTableRowNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Could not find table row with id={vcs_row_id}.',
        )
    except exceptions.MarketInputAlreadyExistException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Market input already exist for vcs row with id={vcs_row_id}.',
        )
'''


def update_market_input(market_input_id: int, project_id: int, market_input: models.MarketInputPost) -> bool:
    try:
        with get_connection() as con:
            db_result = storage.update_market_input(con, market_input_id, project_id, market_input)
            con.commit()
            return db_result
    except auth_ex.UnauthorizedOperationException:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Unauthorized user.',
        )
    except exceptions.MarketInputNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Could not find market input with id={market_input_id}',
        )
    except exceptions.WrongTimeUnitException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Time unit has to be one of [year, month, week, day, hour]. Submitted value was: {e.time_unit}'
        )

def delete_market_input(mi_id: int) -> bool:
    try:
        with get_connection() as con:
            res = storage.delete_market_input(con, mi_id)
            con.commit()
            return res
    except exceptions.MarketInputFailedDeletionException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Could not delete market input with id: {mi_id}'
        )

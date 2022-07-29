from typing import List

from fastapi import HTTPException
from starlette import status

from sedbackend.apps.core.authentication import exceptions as auth_ex
from sedbackend.apps.core.db import get_connection
from sedbackend.apps.cvs.vcs import exceptions as vcs_exceptions
from sedbackend.apps.cvs.market_input import models, storage, exceptions


def get_all_market_inputs(vcs_id: int) -> List[models.MarketInputGet]:
    try:
        with get_connection() as con:
            db_result = storage.get_all_market_input(con, vcs_id)
            con.commit()
            return db_result
    except auth_ex.UnauthorizedOperationException:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Unauthorized user.',
        )
    except vcs_exceptions.VCSNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Could not find vcs with id={vcs_id}.',
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


def update_market_input(vcs_row_id: int, market_input: models.MarketInputPost) -> bool:
    try:
        with get_connection() as con:
            db_result = storage.update_market_input(con, vcs_row_id, market_input)
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
            detail=f'Could not find market input with vcs row id={vcs_row_id}',
        )
    except exceptions.WrongTimeUnitException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Time unit has to be one of [year, month, week, day, hour]. Submitted value was: {e.time_unit}'
        )

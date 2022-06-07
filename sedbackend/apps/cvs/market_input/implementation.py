from typing import List

from fastapi import HTTPException
from starlette import status

from sedbackend.apps.core.authentication import exceptions as auth_ex
from sedbackend.apps.core.db import get_connection
from sedbackend.apps.cvs.project import exceptions as project_exceptions
from sedbackend.apps.cvs.vcs import exceptions as vcs_exceptions
from sedbackend.apps.cvs.market_input import models, storage, exceptions


def get_all_market_inputs(project_id: int, vcs_id: int, user_id: int) -> List[
    models.MarketInputGet]:
    try:
        with get_connection() as con:
            db_result = storage.get_all_market_input(con, project_id, vcs_id, user_id)
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
    except project_exceptions.CVSProjectNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Could not find project with id={project_id}.',
        )


def create_market_input(project_id: int, vcs_id: int, node_id: int, market_input: models.MarketInputPost,
                        user_id: int) -> models.MarketInputGet:
    try:
        with get_connection() as con:
            db_result = storage.create_market_input(con, project_id, vcs_id, node_id, market_input, user_id)
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
    except project_exceptions.CVSProjectNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Could not find project with id={project_id}.',
        )
    except vcs_exceptions.VCSTableRowNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Could not find table row with node_id={node_id}.',
        )
    except exceptions.MarketInputAlreadyExistException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Market input already exist for bpmn node with id={node_id}.',
        )


def update_market_input(project_id: int, vcs_id: int, node_id: int, market_input: models.MarketInputPost,
                        user_id) -> models.MarketInputGet:
    try:
        with get_connection() as con:
            db_result = storage.update_market_input(con, project_id, vcs_id, node_id, market_input, user_id)
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
    except project_exceptions.CVSProjectNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Could not find project with id={project_id}.',
        )
    except exceptions.MarketInputNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Could not find market input with id={node_id}',
        )
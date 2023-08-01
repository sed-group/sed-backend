from typing import List

from fastapi import HTTPException
from starlette import status

from sedbackend.apps.core.authentication import exceptions as auth_ex
from sedbackend.apps.core.db import get_connection
from sedbackend.apps.cvs.project import exceptions as proj_exceptions
from sedbackend.apps.cvs.market_input import models, storage, exceptions
from sedbackend.apps.cvs.vcs import exceptions as vcs_exceptions


########################################################################################################################
# Market Inputs
########################################################################################################################


def get_all_external_factors(project_id: int) -> List[models.ExternalFactor]:
    try:
        with get_connection() as con:
            db_result = storage.get_all_external_factors(con, project_id)
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
    except exceptions.ExternalFactorNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Could not find market input',
        )


def get_external_factor(project_id: int, external_factor_id: int) -> models.ExternalFactor:
    try:
        with get_connection() as con:
            db_result = storage.get_external_factor(con, project_id, external_factor_id)
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
    except exceptions.ExternalFactorNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Could not find market input',
        )


def create_external_factor(project_id: int, external_factor_post: models.ExternalFactorPost) -> models.ExternalFactor:
    try:
        with get_connection() as con:
            db_result = storage.create_external_factor(con, project_id, external_factor_post)
            con.commit()
            return db_result
    except auth_ex.UnauthorizedOperationException:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Unauthorized user.',
        )


def update_external_factor(project_id: int, external_factor: models.ExternalFactor) -> bool:
    try:
        with get_connection() as con:
            db_result = storage.update_external_factor(con, project_id, external_factor)
            con.commit()
            return db_result
    except auth_ex.UnauthorizedOperationException:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Unauthorized user.',
        )
    except exceptions.ExternalFactorNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Could not find external factor with id={external_factor.id}',
        )
    except proj_exceptions.CVSProjectNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Could not find project with id={project_id}.',
        )
    except proj_exceptions.CVSProjectNoMatchException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'External factor with id={external_factor.id} is not a part from project with id={project_id}.',
        )


def delete_external_factor(project_id: int, external_factor_id: int) -> bool:
    try:
        with get_connection() as con:
            res = storage.delete_external_factor(con, project_id, external_factor_id)
            con.commit()
            return res
    except exceptions.ExternalFactorFailedDeletionException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Could not delete market input with id: {external_factor_id}'
        )
    except proj_exceptions.CVSProjectNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Could not find project with id={project_id}.',
        )
    except proj_exceptions.CVSProjectNoMatchException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Market input with id={external_factor_id} is not a part from project with id={project_id}.',
        )


def get_all_formula_market_inputs(formulas_id: int) -> List[models.ExternalFactor]:
    try:
        with get_connection() as con:
            res = storage.get_all_formula_external_factors(con, formulas_id)
            con.commit()
            return res
    except exceptions.ExternalFactorAlreadyExistException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Could not find market inputs for formula with vcs_row id: {formulas_id}'
        )


########################################################################################################################
# Market Values
########################################################################################################################


def update_market_input_value(project_id: int, mi_value: models.ExternalFactorValue) -> bool:
    try:
        with get_connection() as con:
            res = storage.update_external_factor_value(con, project_id, mi_value)
            con.commit()
            return res
    except exceptions.ExternalFactorNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Could not find market input with id={mi_value.market_input_id}.',
        )
    except vcs_exceptions.VCSNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Could not find vcs with id={mi_value.vcs_id}.',
        )
    except proj_exceptions.CVSProjectNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Could not find project with id={project_id}.',
        )
    except proj_exceptions.CVSProjectNoMatchException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Market input with id={mi_value.market_input_id} is not a part from project with id={project_id}.',
        )


def update_external_factor_values(project_id: int, external_factor_values: List[models.ExternalFactorValue]) -> bool:
    try:
        with get_connection() as con:
            res = storage.update_external_factor_values(con, project_id, external_factor_values)
            con.commit()
            return res
    except exceptions.ExternalFactorNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Could not find market input',
        )
    except vcs_exceptions.VCSNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Could not find vcs',
        )
    except proj_exceptions.CVSProjectNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Could not find project with id={project_id}.',
        )


def get_all_external_factor_values(project_id: int) -> List[models.ExternalFactorValue]:
    try:
        with get_connection() as con:
            res = storage.get_all_external_factor_values(con, project_id)
            con.commit()
            return res
    except proj_exceptions.CVSProjectNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Could not find project with id={project_id}.',
        )


def delete_external_factor_value(project_id: int, vcs_id: int, external_factor_id: int) -> bool:
    try:
        with get_connection() as con:
            res = storage.delete_external_factor_value(con, project_id, vcs_id, external_factor_id)
            con.commit()
            return res
    except exceptions.ExternalFactorFailedDeletionException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Could not delete external factor value with external factor id: {external_factor_id} and vcs id: {vcs_id}'
        )
    except proj_exceptions.CVSProjectNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Could not find project with id={project_id}.',
        )
    except proj_exceptions.CVSProjectNoMatchException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'External factor with id={external_factor_id} is not a part from project with id={project_id}.',
        )

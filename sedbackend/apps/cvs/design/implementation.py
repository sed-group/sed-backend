from typing import List

from fastapi import HTTPException
from starlette import status

import sedbackend.apps.cvs.vcs.exceptions as vcs_exceptions
import sedbackend.apps.cvs.project.exceptions as project_exceptions
from sedbackend.apps.core.authentication import exceptions as auth_ex
from sedbackend.apps.core.db import get_connection
from sedbackend.apps.cvs.design import models, storage, exceptions
from sedbackend.apps.cvs.vcs.models import ValueDriver


# ======================================================================================================================
# CVS Design Group
# ======================================================================================================================


def create_cvs_design_group(design_group_post: models.DesignGroupPost, project_id: int) -> models.DesignGroup:
    try:
        with get_connection() as con:
            result = storage.create_design_group(con, design_group_post, project_id)
            con.commit()
            return result
    except project_exceptions.CVSProjectNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Could not find project.',
        )
    except exceptions.DesignGroupInsertException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Could not add value drivers to design group'
        )
    except auth_ex.UnauthorizedOperationException:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Unauthorized user.',
        )

def get_all_design_groups(project_id: int) -> List[models.DesignGroup]:
    try:
        with get_connection() as con:
            res = storage.get_all_design_groups(con, project_id)
            con.commit()
            return res
    except project_exceptions.CVSProjectNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Could not find project.',
        )
    except auth_ex.UnauthorizedOperationException:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Unauthorized user.',
        )


def get_design_group(design_group_id: int) -> models.DesignGroup:
    try:
        with get_connection() as con:
            result = storage.get_design_group(con, design_group_id)
            con.commit()
            return result
    except project_exceptions.CVSProjectNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Could not find project.',
        )
    except auth_ex.UnauthorizedOperationException:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Unauthorized user.',
        )
    except exceptions.DesignGroupNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Could not find design with id={design_group_id}.',
        )


def delete_design_group(design_group_id: int) -> bool:
    try:
        with get_connection() as con:
            res = storage.delete_design_group(con, design_group_id)
            con.commit()
            return res
    except project_exceptions.CVSProjectFailedDeletionException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Could not find project.',
        )
    except project_exceptions.CVSProjectNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Could not find project.'
        )
    except exceptions.DesignGroupNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Could not find design with id={design_group_id}.',
        )


def edit_design_group(design_group_id: int, updated_design: models.DesignGroupPost) -> models.DesignGroup:
    try:
        with get_connection() as con:
            result = storage.edit_design_group(con, design_group_id, updated_design)
            con.commit()
            return result
    except project_exceptions.CVSProjectNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Could not find project.'
        )
    except exceptions.DesignGroupNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Could not find design group with id={design_group_id}.',
        )
    except vcs_exceptions.VCSNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Could not find vcs.',
        )


# ======================================================================================================================
# CVS Design
# ======================================================================================================================

def get_design(design_id: int) -> models.Design:
    try:
        with get_connection() as con:
            res = storage.get_design(con, design_id)
            con.commit()
            return res
    except exceptions.DesignNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Could not find design'
        )


def get_all_designs(design_group_id: int) -> List[models.Design]:
    try:
        with get_connection() as con:
            res = storage.get_all_designs(con, design_group_id)
            con.commit()
            return res
    except exceptions.DesignGroupNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Could not find design group'
        )


def edit_designs(design_group_id: int, designs: List[models.DesignPut]) -> bool:
    try:
        with get_connection() as con:
            res = storage.edit_designs(con, design_group_id, designs)
            con.commit()
            return res
    except exceptions.DesignNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Could not find design'
        )
    except exceptions.QuantifiedObjectiveValueNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Could not find quantified objective value'
        )
    except exceptions.DesignGroupNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Could not find design group'
        )
    except exceptions.DesignInsertException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Could not insert the values provided'
        )


def get_all_formula_value_drivers(formula_id: int) -> List[models.ValueDriver]:
    try:
        with get_connection() as con:
            res = storage.get_all_formula_value_drivers(con, formula_id)
            con.commit()
            return res
    except exceptions.DesignNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Could not find design'
        )

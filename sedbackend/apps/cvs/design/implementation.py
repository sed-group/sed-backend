from typing import List

from fastapi import HTTPException
from starlette import status

import sedbackend.apps.cvs.vcs.exceptions as vcs_exceptions
import sedbackend.apps.cvs.project.exceptions as project_exceptions
from sedbackend.apps.core.authentication import exceptions as auth_ex
from sedbackend.apps.core.db import get_connection
from sedbackend.apps.cvs.design import models, storage, exceptions


# ======================================================================================================================
# CVS Design Group
# ======================================================================================================================


def create_cvs_design_group(design_group_post: models.DesignGroupPost, vcs_id: int) -> models.DesignGroup:
    try:
        with get_connection() as con:
            result = storage.create_design_group(con, design_group_post, vcs_id)
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
    except vcs_exceptions.VCSNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Could not find vcs with id={vcs_id}.',
        )


def get_all_design_groups(vcs_id: int) -> List[models.DesignGroup]:
    try:
        with get_connection() as con:
            return storage.get_all_design_groups(con, vcs_id)
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
    except vcs_exceptions.VCSNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Could not find vcs with id={vcs_id}.',
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
    except vcs_exceptions.VCSNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Could not find vcs.',
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
    except vcs_exceptions.VCSNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Could not find vcs.',
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
    except exceptions.DesignNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Could not find design with id={design_group_id}.',
        )
    except vcs_exceptions.VCSNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Could not find vcs.',
        )


# ======================================================================================================================
# CVS Design Group
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


def create_design(design_group_id: int, design: models.DesignPost) -> bool:
    try:
        with get_connection() as con:
            res = storage.create_design(con, design_group_id, design)
            con.commit()
            return res
    except exceptions.DesignGroupNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Could not find design group'
        )


def edit_design(design_id: int, design: models.DesignPost) -> bool:
    try:
        with get_connection() as con:
            res = storage.edit_design(con, design_id, design)
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


def delete_design(design_id) -> bool:
    try:
        with get_connection() as con:
            res = storage.delete_design(con, design_id)
            con.commit()
            return res
    except exceptions.DesignNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Could not find design'
        )


# ======================================================================================================================
# Quantified Objectives
# ======================================================================================================================


def get_all_quantified_objectives(design_group_id: int) -> List[models.QuantifiedObjective]:
    try:
        with get_connection() as con:
            res = storage.get_all_quantified_objectives(con, design_group_id)
            con.commit()
            return res
    except exceptions.QuantifiedObjectiveNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Could not find quantified objective'
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
    except vcs_exceptions.VCSNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Could not find vcs.',
        )


def get_quantified_objective(value_driver_id: int, design_group_id: int) -> models.QuantifiedObjective:
    try:
        with get_connection() as con:
            res = storage.get_quantified_objective(con, value_driver_id, design_group_id)
            con.commit()
            return res
    except exceptions.QuantifiedObjectiveNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Could not find quantified objective value driver id={value_driver_id} '
                   f'and design id = {design_group_id}'
        )
    except project_exceptions.CVSProjectNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Could not find project.'
        )
    except exceptions.DesignNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Could not find design.',
        )
    except vcs_exceptions.VCSNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Could not find vcs.',
        )
    except vcs_exceptions.ValueDriverNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Could not find value driver.',
        )


def create_quantified_objective(design_group_id: int, value_driver_id: int,
                                quantified_objective_post: models.QuantifiedObjectivePost) \
        -> bool:
    try:
        with get_connection() as con:
            res = storage.create_quantified_objective(con, design_group_id, value_driver_id, quantified_objective_post)
            con.commit()
            return res
    except project_exceptions.CVSProjectNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Could not find project.'
        )
    except vcs_exceptions.ValueDriverNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Could not find value driver with id={value_driver_id}.',
        )


def delete_quantified_objective(value_driver_id: int, design_group_id: int) -> bool:
    try:
        with get_connection() as con:
            res = storage.delete_quantified_objective(con, value_driver_id, design_group_id)
            con.commit()
            return res
    except auth_ex.UnauthorizedOperationException:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Unauthorized operation'
        )
    except exceptions.QuantifiedObjectiveNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Could not find quantified objective'
        )
    except project_exceptions.CVSProjectNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Could not find project.'
        )
    except exceptions.DesignGroupNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Could not find design.',
        )
    except vcs_exceptions.VCSNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Could not find vcs.',
        )
    except vcs_exceptions.ValueDriverNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Could not find value driver.',
        )


def edit_quantified_objective(value_driver_id: int, design_group_id: int,
                              updated_qo: models.QuantifiedObjectivePost) -> models.QuantifiedObjective:
    try:
        with get_connection() as con:
            res = storage.edit_quantified_objective(con, value_driver_id, design_group_id, updated_qo)
            con.commit()
            return res
    except exceptions.QuantifiedObjectiveNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Could not find quantified objective.'
        )
    except project_exceptions.CVSProjectNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Could not find project.'
        )
    except exceptions.DesignGroupNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Could not find design.',
        )
    except vcs_exceptions.VCSNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Could not find vcs.',
        )

def get_all_formula_quantified_objectives(formulas_id: int) -> List[models.QuantifiedObjective]:
    try:
        with get_connection() as con:
            res = storage.get_all_formula_quantified_objectives(con, formulas_id)
            con.commit()
            return res
    except exceptions.QuantifiedObjectiveNotInFormulas:
        raise HTTPException(
             status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Could not find quantified objectives for formula'
        )
    except exceptions.DesignGroupNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Could not find design.',
        )
    except vcs_exceptions.ValueDriverNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Could not find value driver.',
        )
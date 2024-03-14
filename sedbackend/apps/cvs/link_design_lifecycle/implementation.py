from typing import List
from fastapi import HTTPException
from starlette import status
from sedbackend.apps.core.db import get_connection
from sedbackend.apps.cvs.link_design_lifecycle import models, storage
from sedbackend.apps.cvs.link_design_lifecycle import exceptions
from sedbackend.apps.cvs.project import exceptions as project_exceptions
from sedbackend.apps.cvs.design import exceptions as design_exceptions
from sedbackend.apps.cvs.vcs import exceptions as vcs_exceptions


def edit_formulas(project_id: int, vcs_id: int, design_group_id: int, formulas: List[models.FormulaRowPost]) -> bool:
    with get_connection() as con:
        try:
            res = storage.update_formulas(con, project_id, vcs_id, design_group_id, formulas)
            con.commit()
            return res
        except vcs_exceptions.VCSNotFoundException:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'Could not find vcs'
            )
        except exceptions.FormulasFailedUpdateException:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f'No formulas updated. Are the formulas changed?'
            )
        except exceptions.TooManyFormulasUpdatedException:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f'Too many formulas tried to be updated.'
            )
        except design_exceptions.DesignGroupNotFoundException:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'Could not find design group with id {design_group_id}'
            )
        except project_exceptions.CVSProjectNotFoundException:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'Could not find project with id {project_id}'
            )
        except project_exceptions.CVSProjectNoMatchException:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f'Project with id={project_id} does not match design group with id={design_group_id}'
            )
        except vcs_exceptions.VCSTableRowNotFoundException:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'Could not find vcs row.',
            )
        except exceptions.CouldNotAddValueDriverToProjectException:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f'Failed to add value driver from another project'
            )


def get_all_formulas(project_id: int, vcs_id: int, design_group_id: int) -> List[models.FormulaRowGet]:
    with get_connection() as con:
        try:
            res = storage.get_all_formulas(con, project_id, vcs_id, design_group_id)
            con.commit()
            return res
        except vcs_exceptions.VCSNotFoundException:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'Could not find VCS with id {vcs_id}'
            )
        except project_exceptions.CVSProjectNotFoundException:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'Could not find project with id {project_id}'
            )
        except project_exceptions.CVSProjectNoMatchException:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f'Project id {project_id} does not match with vcs id {vcs_id}'
            )


def delete_formulas(project_id: int, vcs_row_id: int, design_group_id: int) -> bool:
    with get_connection() as con:
        try:
            res = storage.delete_formulas(con, project_id, vcs_row_id, design_group_id)
            con.commit()
            return res
        except exceptions.FormulasFailedDeletionException:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f'Could not delete formulas with row id: {vcs_row_id}'
            )
        except project_exceptions.CVSProjectNotFoundException:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'Could not find project with id {project_id}'
            )
        except project_exceptions.CVSProjectNoMatchException:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f'Project with id={project_id} does not match design group with id={design_group_id}'
            )
        except design_exceptions.DesignGroupNotFoundException:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f'Could not find design with id={design_group_id}.',
            )
        except vcs_exceptions.VCSTableRowNotFoundException:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'Could not find vcs row with id={vcs_row_id}.',
            )


def get_vcs_dg_pairs(project_id: int) -> List[models.VcsDgPairs]:
    with get_connection() as con:
        try:
            res = storage.get_vcs_dg_pairs(con, project_id)
            con.commit()
            return res
        except project_exceptions.CVSProjectNotFoundException:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'Could not find project with id {project_id}'
            )

from typing import List

from fastapi import HTTPException, UploadFile
from starlette import status

from sedbackend.apps.core.applications.exceptions import ApplicationNotFoundException
from sedbackend.apps.core.authentication import exceptions as auth_ex
from sedbackend.apps.core.db import get_connection
from sedbackend.apps.cvs.vcs import exceptions as vcs_exceptions
from sedbackend.apps.cvs.life_cycle import exceptions, storage, models
from sedbackend.apps.cvs.project import exceptions as project_exceptions
from sedbackend.apps.core.files import models as file_models, exceptions as file_ex
import sedbackend.apps.core.projects.exceptions as core_project_exceptions


def create_process_node(project_id: int, vcs_id: int, node: models.ProcessNodePost) -> models.ProcessNodeGet:
    try:
        with get_connection() as con:
            result = storage.create_process_node(con, project_id, vcs_id, node)
            con.commit()
            return result
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


def create_start_stop_node(node: models.StartStopNodePost, vcs_id: int) -> models.StartStopNodeGet:
    try:
        with get_connection() as con:
            result = storage.create_start_stop_node(con, node, vcs_id)
            con.commit()
            return result
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
    except exceptions.InvalidNodeType:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Type must be start or stop.',
        )


def delete_node(project_id: int, node_id: int) -> bool:
    try:
        with get_connection() as con:
            result = storage.delete_node(con, project_id, node_id)
            con.commit()
            return result

    except exceptions.NodeNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Could not find node with id={node_id}.',
        )
    except exceptions.NodeFailedDeletionException as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'Failed to remove node with id={e.node_id}.',
        )
    except project_exceptions.CVSProjectNoMatchException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Node with id={node_id} is not a part of project with id={project_id}.',
        )


def update_node(project_id: int, node_id: int, node: models.NodePost) -> bool:
    try:
        with get_connection() as con:
            result = storage.update_node(con, project_id, node_id, node)
            con.commit()
            return result
    except exceptions.NodeNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Could not find node with id={node_id}.',
        )
    except exceptions.NodeFailedToUpdateException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Failed to update node.',
        )
    except auth_ex.UnauthorizedOperationException:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Unauthorized user.',
        )
    except project_exceptions.CVSProjectNoMatchException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Node with id={node_id} is not a part of project with id={project_id}.',
        )


def get_bpmn(project_id: int, vcs_id: int) -> models.BPMNGet:
    try:
        with get_connection() as con:
            result = storage.get_bpmn(con, project_id, vcs_id)
            con.commit()
            return result
    except vcs_exceptions.VCSNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Could not find vcs with id={vcs_id}.',
        )
    except auth_ex.UnauthorizedOperationException:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Unauthorized user.',
        )
    except project_exceptions.CVSProjectNoMatchException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Project with id={project_id} is not a part of vcs with id={vcs_id}.',
        )


def update_bpmn(project_id: int, vcs_id: int, bpmn: models.BPMNGet) -> bool:
    try:
        with get_connection() as con:
            result = storage.update_bpmn(con, project_id, vcs_id, bpmn)
            con.commit()
            return result
    except vcs_exceptions.VCSNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Could not find vcs with id={vcs_id}.',
        )
    except exceptions.NodeNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Could not find node.',
        )
    except exceptions.NodeFailedToUpdateException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Failed to update node.',
        )
    except auth_ex.UnauthorizedOperationException:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Unauthorized user.',
        )
    except project_exceptions.CVSProjectNoMatchException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Project with id={project_id} is not a part of vcs with id={vcs_id}.',
        )


def save_dsm_file(project_id: int, vcs_id: int,
                  file: UploadFile, user_id: int) -> bool:
    try:
        with get_connection() as con:
            result = storage.save_dsm_file(con, project_id, vcs_id, file, user_id)
            con.commit()
            return result
    except exceptions.InvalidFileTypeException:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail='Wrong filetype'
        )
    except exceptions.FileSizeException:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail='File too large'
        )
    except exceptions.ProcessesVcsMatchException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Processes in DSM does not match processes in VCS'
        )
    except core_project_exceptions.SubProjectNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sub-project not found."
        )
    except ApplicationNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No such application."
        )
    except exceptions.DSMFileFailedDeletionException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to replace old DSM file."
        )


def save_dsm(project_id: int, vcs_id: int,
             dsm: List[List[str or float]], user_id: int) -> bool:
    try:
        with get_connection() as con:
            result = storage.save_dsm_matrix(con, project_id, vcs_id, dsm, user_id)
            con.commit()
            return result
    except exceptions.InvalidFileTypeException:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail='Wrong filetype'
        )
    except exceptions.FileSizeException:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail='File too large'
        )
    except exceptions.ProcessesVcsMatchException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Processes in DSM does not match processes in VCS'
        )
    except core_project_exceptions.SubProjectNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sub-project not found."
        )
    except ApplicationNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No such application."
        )
    except exceptions.DSMFileFailedDeletionException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to replace old DSM file."
        )


def get_dsm_file_id(project_id: int, vcs_id: int) -> int:
    try:
        with get_connection() as con:
            res = storage.get_dsm_file_id(con, project_id, vcs_id)
            con.commit()
            return res
    except file_ex.FileNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"File could not be found"
        )


def get_dsm_file_path(project_id: int, vcs_id: int, user_id) -> file_models.StoredFilePath:
    try:
        with get_connection() as con:
            res = storage.get_dsm_file_path(con, project_id, vcs_id, user_id)
            con.commit()
            return res
    except file_ex.FileNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"File could not be found"
        )
    except auth_ex.UnauthorizedOperationException:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"User does not have access to the file"
        )


def get_dsm(project_id: int, vcs_id: int, user_id: int) -> List[List[str or float]]:
    try:
        with get_connection() as con:
            res = storage.get_dsm(con, project_id, vcs_id, user_id)
            con.commit()
            return res
    except file_ex.FileNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"File could not be found"
        )
    except auth_ex.UnauthorizedOperationException:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"User does not have access to the file"
        )

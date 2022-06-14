from fastapi import HTTPException
from starlette import status

from sedbackend.apps.core.authentication import exceptions as auth_ex
from sedbackend.apps.core.db import get_connection
from sedbackend.apps.cvs.vcs import exceptions as vcs_exceptions
from sedbackend.apps.cvs.life_cycle import exceptions, storage, models


def create_process_node(node: models.ProcessNodePost, vcs_id: int) -> models.ProcessNodeGet:
    try:
        with get_connection() as con:
            result = storage.create_process_node(con, node, vcs_id)
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


def delete_node(node_id: int, vcs_id: int) -> bool:
    try:
        with get_connection() as con:
            result = storage.delete_node(con, node_id)
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
            detail=f'Could not find node with id={node_id}.',
        )
    except exceptions.NodeFailedDeletionException as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'Failed to remove node with id={e.node_id}.',
        )


def update_node(node_id: int, node: models.NodePost, vcs_id: int) -> bool:
    try:
        with get_connection() as con:
            result = storage.update_node(con, node_id, node)
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
            detail=f'Could not find node with id={node_id}.',
        )
    except auth_ex.UnauthorizedOperationException:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Unauthorized user.',
        )


def get_bpmn(vcs_id: int) -> models.BPMNGet:
    try:
        with get_connection() as con:
            result = storage.get_bpmn(con, vcs_id)
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


def update_bpmn(vcs_id: int, bpmn: models.BPMNGet) -> bool:
    try:
        with get_connection() as con:
            result = storage.update_bpmn(con, vcs_id, bpmn)
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

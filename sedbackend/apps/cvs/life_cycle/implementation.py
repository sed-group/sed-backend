from typing import List

from fastapi import HTTPException
from starlette import status

from sedbackend.apps.core.authentication import exceptions as auth_ex
from sedbackend.apps.core.db import get_connection
from sedbackend.apps.cvs.project import exceptions as project_exceptions
from sedbackend.apps.cvs.vcs import exceptions as vcs_exceptions
from sedbackend.apps.cvs.life_cycle import exceptions, storage, models


def create_bpmn_node(node: models.NodePost, project_id: int, vcs_id: int, user_id: int) -> models.NodeGet:
    try:
        with get_connection() as con:
            result = storage.create_bpmn_node(con, node, project_id, vcs_id, user_id)
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
    except project_exceptions.CVSProjectNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Could not find project with id={project_id}.',
        )


def delete_bpmn_node(node_id: int, project_id: int, vcs_id: int, user_id: int) -> bool:
    try:
        with get_connection() as con:
            result = storage.delete_bpmn_node(con, project_id, vcs_id, node_id, user_id)
            con.commit()
            return result

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


def update_bpmn_node(node_id: int, node: models.NodePost, project_id: int, vcs_id: int, user_id: int) -> models.NodeGet:
    try:
        with get_connection() as con:
            result = storage.update_bpmn_node(con, node_id, node, project_id, vcs_id, user_id)
            con.commit()
            return result
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


def create_bpmn_edge(edge: models.EdgePost, project_id, vcs_id, user_id) -> models.EdgeGet:
    try:
        with get_connection() as con:
            result = storage.create_bpmn_edge(con, edge, project_id, vcs_id, user_id)
            con.commit()
            return result
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
    except auth_ex.UnauthorizedOperationException:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Unauthorized user.',
        )
    except exceptions.NodeNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Could not find node with id = {edge.from_node} or {edge.to_node}.',
        )


def delete_bpmn_edge(edge_id: int, project_id, vcs_id, user_id) -> bool:
    try:
        with get_connection() as con:
            result = storage.delete_bpmn_edge(con, edge_id, project_id, vcs_id, user_id)
            con.commit()
            return result

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
    except exceptions.EdgeNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Could not find edge with id={edge_id}.',
        )
    except exceptions.EdgeFailedDeletionException as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'Failed to remove edge with id={e.edge_id}.',
        )
    except auth_ex.UnauthorizedOperationException:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Unauthorized user.',
        )


def update_bpmn_edge(edge_id: int, edge: models.EdgePost, project_id: int, vcs_id: int, user_id: int) -> models.EdgeGet:
    try:
        with get_connection() as con:
            result = storage.update_bpmn_edge(con, edge_id, edge, project_id, vcs_id, user_id)
            con.commit()
            return result
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
    except exceptions.EdgeNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Could not find edge with id={edge_id}.',
        )
    except exceptions.NodeNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Could not find node with id={edge.from_node} or {edge.to_node}.',
        )
    except auth_ex.UnauthorizedOperationException:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Unauthorized user.',
        )


def get_bpmn(vcs_id: int, project_id: int, user_id: int) -> models.BPMNGet:
    try:
        with get_connection() as con:
            result = storage.get_bpmn(con, vcs_id, project_id, user_id)
            con.commit()
            return result
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
    except auth_ex.UnauthorizedOperationException:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Unauthorized user.',
        )


def update_bpmn(vcs_id: int, project_id: int, user_id: int, nodes: List[models.NodeGet],
                edges: List[
                    models.EdgeGet]) -> models.BPMNGet:
    try:
        with get_connection() as con:
            result = storage.update_bpmn(con, vcs_id, project_id, user_id, nodes, edges)
            con.commit()
            return result
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
    except auth_ex.UnauthorizedOperationException:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Unauthorized user.',
        )

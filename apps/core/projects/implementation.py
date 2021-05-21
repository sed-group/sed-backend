from fastapi import HTTPException, status

from apps.core.projects.exceptions import ProjectNotFoundException, SubProjectNotFoundException
from apps.core.projects.storage import *
from apps.core.db import get_connection
from apps.core.projects.models import AccessLevel, ProjectPost


def impl_get_projects(segment_length: int, index: int):
    with get_connection() as con:
        return db_get_projects(con, segment_length, index)


def impl_get_user_projects(segment_length:int, index: int, user_id: int):
    with get_connection() as con:
        return db_get_user_projects(con, segment_length, index, user_id)


def impl_get_project(project_id: int):
    try:
        with get_connection() as con:
            return db_get_project(con, project_id)
    except ProjectNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )


def impl_get_sub_project(sub_project_id: int):
    try:
        with get_connection() as con:
            return db_get_sub_project(con, sub_project_id)
    except SubProjectNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sub project not found"
        )


def impl_post_project(project: ProjectPost):
    with get_connection() as con:
        res = db_post_project(con, project)
        con.commit()
        return res


def impl_delete_project(project_id: int):
    try:
        with get_connection() as con:
            res = db_delete_project(con, project_id)
            con.commit()
            return res
    except ProjectNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )


def impl_post_participant(project_id: int, user_id: int, access_level: AccessLevel):
    try:
        with get_connection() as con:
            res = db_add_participant(con, project_id, user_id, access_level)
            con.commit()
            return res
    except ProjectNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )


def impl_delete_participant(project_id: int, user_id: int):
    try:
        with get_connection() as con:
            res = db_delete_participant(con, project_id, user_id)
            con.commit()
            return res
    except ProjectNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )


def impl_put_name(project_id: int, name: str):
    try:
        with get_connection() as con:
            res = db_put_name(con, project_id, name)
            con.commit()
            return res
    except ProjectNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

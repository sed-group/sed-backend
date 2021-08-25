from typing import Optional, List

from fastapi import HTTPException, status

from apps.core.applications.exceptions import ApplicationNotFoundException
import apps.core.projects.storage as storage
import apps.core.users.storage as storage_users
import apps.core.users.exceptions as exc_users
from apps.core.db import get_connection
import apps.core.projects.models as models
import apps.core.projects.exceptions as exc


def impl_get_projects(segment_length: int, index: int):
    with get_connection() as con:
        return storage.db_get_projects(con, segment_length, index)


def impl_get_user_projects(user_id: int, segment_length: int = 0, index: int = 0) -> List[models.ProjectListing]:
    with get_connection() as con:
        return storage.db_get_user_projects(con, user_id, segment_length=segment_length, index=index)


def impl_get_project(project_id: int) -> models.Project:
    try:
        with get_connection() as con:
            return storage.db_get_project(con, project_id)
    except exc.ProjectNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )


def impl_post_project(project: models.ProjectPost, owner_id: int) -> models.Project:
    try:
        with get_connection() as con:
            # Assert that all participants exist
            storage_users.db_get_users_with_ids(con, project.participants)

            res = storage.db_post_project(con, project, owner_id)
            con.commit()
            return res
    except exc.ParticipantInconsistencyException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except exc_users.UserNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


def impl_delete_project(project_id: int) -> bool:
    try:
        with get_connection() as con:
            res = storage.db_delete_project(con, project_id)
            con.commit()
            return res
    except exc.ProjectNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )


def impl_post_participant(project_id: int, user_id: int, access_level: models.AccessLevel) -> bool:
    try:
        with get_connection() as con:
            res = storage.db_add_participant(con, project_id, user_id, access_level)
            con.commit()
            return res
    except exc.ProjectNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )


def impl_delete_participant(project_id: int, user_id: int) -> bool:
    try:
        with get_connection() as con:
            res = storage.db_delete_participant(con, project_id, user_id)
            con.commit()
            return res
    except exc.ProjectNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )
    except exc.ParticipantChangeException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No participant deleted. The participant could not be found."
        )


def impl_put_name(project_id: int, name: str) -> bool:
    try:
        with get_connection() as con:
            res = storage.db_put_name(con, project_id, name)
            con.commit()
            return res
    except exc.ProjectNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )


def impl_post_subproject(subproject: models.SubProjectPost, current_user_id: int, project_id: Optional[int] = None) \
        -> models.SubProject:
    try:
        with get_connection() as con:
            res = storage.db_post_subproject(con, subproject, current_user_id, project_id)
            con.commit()
            return res
    except exc.ProjectNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    except exc.SubProjectDuplicateException:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Subproject with same native id and application sid already exists."
        )


def impl_get_subprojects(project_id: int) -> List[models.SubProject]:
    with get_connection() as con:
        return storage.db_get_subprojects(con, project_id)


def impl_get_subproject(project_id: int, subproject_id: int) -> models.SubProject:
    try:
        with get_connection() as con:
            return storage.db_get_subproject(con, project_id, subproject_id)
    except exc.SubProjectNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sub project not found"
        )
    except exc.ProjectNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )


def impl_get_subproject_native(application_sid: str, native_project_id: int) -> models.SubProject:
    try:
        with get_connection() as con:
            return storage.db_get_subproject_native(con, application_sid, native_project_id)
    except exc.SubProjectNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sub project not found"
        )
    except ApplicationNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No such application"
        )


def impl_delete_subproject(project_id: int, subproject_id: int) -> bool:
    try:
        with get_connection() as con:
            res = storage.db_delete_subproject(con, project_id, subproject_id)
            con.commit()
            return res
    except exc.SubProjectNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sub project not found"
        )
    except exc.ProjectNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

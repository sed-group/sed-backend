from typing import Optional, List, Union, Dict

from fastapi import HTTPException, status

from sedbackend.apps.core.applications.exceptions import ApplicationNotFoundException
import sedbackend.apps.core.projects.storage as storage
import sedbackend.apps.core.users.storage as storage_users
import sedbackend.apps.core.users.exceptions as exc_users
from sedbackend.apps.core.db import get_connection
import sedbackend.apps.core.projects.models as models
import sedbackend.apps.core.projects.exceptions as exc


def impl_get_projects(user_id: int, segment_length: int = 0, index: int = 0):
    with get_connection() as con:
        return storage.db_get_projects(con, user_id, segment_length, index)


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
            if len(project.participants) > 0:
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
    except exc.ConflictingProjectAssociationException as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
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


def impl_update_project(project_id: int, project_updated: models.ProjectEdit) -> models.Project:
    # Validate input
    if project_id != project_updated.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Conflicting project IDs (payload vs URL)"
        )

    try:
        with get_connection() as con:
            res = storage.db_update_project(con, project_updated)
            con.commit()
            return res
    except exc.ProjectNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Project not found"
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


def impl_post_participants(project_id: int, participants_access_dict: dict[int, models.AccessLevel]) -> bool:
    try:
        with get_connection() as con:
            res = storage.db_add_participants(con, project_id, participants_access_dict)
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
            detail="Sub-project not found."
        )
    except ApplicationNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No such application."
        )


def impl_get_subproject_by_id(subproject_id: int) -> models.SubProject:
    try:
        with get_connection() as con:
            return storage.db_get_subproject_with_id(con, subproject_id)
    except exc.SubProjectNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sub-project not found."
        )


def impl_delete_subproject(project_id: Union[int, None], subproject_id: int) -> bool:
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


def impl_delete_subproject_native(application_id: str, native_project_id: int):
    try:
        with get_connection() as con:
            res = storage.db_delete_subproject_native(con, application_id, native_project_id)
            con.commit()
            return res
    except exc.SubProjectNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No such subproject"
        )


def impl_get_user_subprojects_with_application_sid(current_user_id: int, user_id: int, application_id: str,
                                                   no_project_association: bool = False):
    # This may look redundant, but it is there to prevent devs from accidentally giving access to any user.
    if current_user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User does not have access to this information"
        )

    try:
        with get_connection() as con:
            return storage.db_get_user_subprojects_with_application_sid(con, user_id, application_id,
                                                                        no_project_association=no_project_association)
    except ApplicationNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Application with ID = {application_id} is not available."
        )

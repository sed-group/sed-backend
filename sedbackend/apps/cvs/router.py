from operator import mod
from urllib import response
from sedbackend.libs.datastructures.pagination import ListChunk

from fastapi import APIRouter, Depends
from typing import List

from sedbackend.apps.core.users.models import User
from sedbackend.apps.core.authentication.utils import get_current_active_user

import sedbackend.apps.cvs.implementation as impl
import sedbackend.apps.cvs.models as models

router = APIRouter()

CVS_APP_SID = 'MOD.CVS'


# ======================================================================================================================
# CVS projects
# ======================================================================================================================

@router.get(
    '/project/get/all',
    summary='Returns all of the user\'s CVS projects',
    response_model=ListChunk[models.CVSProject],
)
async def get_all_cvs_project(user: User = Depends(get_current_active_user)) \
        -> ListChunk[models.CVSProject]:
    return impl.get_all_cvs_project(user.id)


@router.get(
    '/project/get/segment',
    summary='Returns a segment of the user\'s CVS projects',
    response_model=ListChunk[models.CVSProject],
)
async def get_segment_cvs_project(index: int, segment_length: int, user: User = Depends(get_current_active_user)) \
        -> ListChunk[models.CVSProject]:
    return impl.get_segment_cvs_project(index, segment_length, user.id)


@router.get(
    '/project/get/{project_id}',
    summary='Returns a CVS project based on id',
    description='Returns a CVS project based on id',
    response_model=models.CVSProject,
)
async def get_csv_project(project_id: int, user: User = Depends(get_current_active_user)) -> models.CVSProject:
    return impl.get_cvs_project(project_id, user.id)


@router.post(
    '/project/create',
    summary='Creates a new CVS project',
    response_model=models.CVSProject,
)
async def create_csv_project(project_post: models.CVSProjectPost,
                             user: User = Depends(get_current_active_user)) -> models.CVSProject:
    return impl.create_cvs_project(project_post, user.id)


@router.put(
    '/project/{project_id}/edit',
    summary='Edits a CVS project',
    response_model=models.CVSProject,
)
async def edit_csv_project(project_id: int, project_post: models.CVSProjectPost,
                           user: User = Depends(get_current_active_user)) -> models.CVSProject:
    return impl.edit_cvs_project(project_id=project_id, user_id=user.id, project_post=project_post)


@router.delete(
    '/project/{project_id}/delete',
    summary='Deletes a CVS project based on id',
    response_model=bool,
)
async def delete_cvs_project(project_id: int, user: User = Depends(get_current_active_user)) -> bool:
    return impl.delete_cvs_project(project_id, user.id)


# ======================================================================================================================
# VCS (Value Creation Strategy)
# ======================================================================================================================

@router.get(
    '/project/{project_id}/vcs/get/all',
    summary='Returns all of VCSs of a project',
    response_model=ListChunk[models.VCS],
)
async def get_all_vcs(project_id: int, user: User = Depends(get_current_active_user)) -> ListChunk[models.VCS]:
    return impl.get_all_vcs(project_id, user.id)


@router.get(
    '/project/{project_id}/vcs/get/segment',
    summary='Returns a segment of the VCSs of a project',
    response_model=ListChunk[models.VCS],
)
async def get_segment_vcs(project_id: int, index: int, segment_length: int,
                          user: User = Depends(get_current_active_user)) -> ListChunk[models.VCS]:
    return impl.get_segment_vcs(project_id, index, segment_length, user.id)


@router.get(
    '/project/{project_id}/vcs/get/{vcs_id}',
    summary='Returns a VCS',
    response_model=models.VCS,
)
async def get_vcs(vcs_id: int, project_id: int, user: User = Depends(get_current_active_user)) -> models.VCS:
    return impl.get_vcs(vcs_id, project_id, user.id)


@router.post(
    '/project/{project_id}/vcs/create',
    summary='Creates a new VCS in a project',
    response_model=models.VCS,
)
async def create_vcs(vcs_post: models.VCSPost, project_id: int,
                     user: User = Depends(get_current_active_user)) -> models.VCS:
    return impl.create_vcs(vcs_post, project_id, user.id)


@router.put(
    '/project/{project_id}/vcs/{vcs_id}/edit',
    summary='Edits a VCS',
    response_model=models.VCS,
)
async def edit_vcs(vcs_id: int, project_id: int, vcs_post: models.VCSPost,
                   user: User = Depends(get_current_active_user)) -> models.VCS:
    return impl.edit_vcs(vcs_id, project_id, user.id, vcs_post)


@router.delete(
    '/project/{project_id}/vcs/{vcs_id}/delete',
    summary='Deletes a VCS based on id',
    response_model=bool,
)
async def delete_vcs(vcs_id: int, project_id: int, user: User = Depends(get_current_active_user)) -> bool:
    return impl.delete_vcs(vcs_id, project_id, user.id)


# ======================================================================================================================
# VCS Value driver
# ======================================================================================================================

@router.get(
    '/project/{project_id}/value-driver/get/all',
    summary='Returns all of value drivers of a project',
    response_model=ListChunk[models.VCSValueDriver],
)
async def get_all_value_driver(project_id: int,
                               user: User = Depends(get_current_active_user)) -> ListChunk[models.VCSValueDriver]:
    return impl.get_all_value_driver(project_id, user.id)


@router.get(
    '/project/{project_id}/value-driver/get/{value_driver_id}',
    summary='Returns a value driver',
    response_model=ListChunk[models.VCSValueDriver],
)
async def get_value_driver(value_driver_id: int, project_id: int,
                           user: User = Depends(get_current_active_user)) -> models.VCSValueDriver:
    return impl.get_value_driver(value_driver_id, project_id, user.id)


@router.post(
    '/project/{project_id}/value-driver/create',
    summary='Creates a new value driver in a project',
    response_model=models.VCSValueDriver,
)
async def create_value_driver(vcs_post: models.VCSValueDriverPost, project_id: int,
                              user: User = Depends(get_current_active_user)) -> models.VCSValueDriver:
    return impl.create_value_driver(vcs_post, project_id, user.id)


@router.put(
    '/project/{project_id}/value-driver/{value_driver_id}/edit',
    summary='Edits a value driver',
    response_model=models.VCSValueDriver,
)
async def edit_value_driver(value_driver_id: int, project_id: int, vcs_post: models.VCSValueDriverPost,
                            user: User = Depends(get_current_active_user)) -> models.VCSValueDriver:
    return impl.edit_value_driver(value_driver_id, project_id, user.id, vcs_post)


@router.delete(
    '/project/{project_id}/value-driver/{value_driver_id}/delete',
    summary='Deletes a value driver',
    response_model=bool,
)
async def delete_value_driver(value_driver_id: int, project_id: int,
                              user: User = Depends(get_current_active_user)) -> bool:
    return impl.delete_value_driver(value_driver_id, project_id, user.id)


# ======================================================================================================================
# VCS ISO Processes
# ======================================================================================================================

@router.get(
    '/vcs/iso-processes/get/all',
    summary='Returns all ISO processes',
    response_model=ListChunk[models.VCSISOProcess],
)
async def get_all_iso_process() -> ListChunk[models.VCSISOProcess]:
    return impl.get_all_iso_process()


# ======================================================================================================================
# VCS Subprocesses
# ======================================================================================================================

@router.get(
    '/project/{project_id}/subprocess/get/all',
    summary='Returns all subprocesses of a project',
    response_model=ListChunk[models.VCSSubprocess],
)
async def get_all_subprocess(project_id: int,
                             user: User = Depends(get_current_active_user)) -> ListChunk[models.VCSSubprocess]:
    return impl.get_all_subprocess(project_id, user.id)


@router.get(
    '/project/{project_id}/subprocess/get/{subprocess_id}',
    summary='Returns a subprocess',
    response_model=ListChunk[models.VCSSubprocess],
)
async def get_subprocess(subprocess_id: int, project_id: int,
                         user: User = Depends(get_current_active_user)) -> models.VCSSubprocess:
    return impl.get_subprocess(subprocess_id, project_id, user.id)


@router.post(
    '/project/{project_id}/subprocess/create',
    summary='Creates a new subprocess',
    response_model=models.VCSSubprocess,
)
async def create_subprocess(subprocess_post: models.VCSSubprocessPost, project_id: int,
                            user: User = Depends(get_current_active_user)) -> models.VCSSubprocess:
    return impl.create_subprocess(subprocess_post, project_id, user.id)


@router.put(
    '/project/{project_id}/subprocess/{subprocess_id}/edit',
    summary='Edits a subprocess',
    response_model=models.VCSSubprocess,
)
async def edit_subprocess(subprocess_id: int, project_id: int, vcs_post: models.VCSSubprocessPost,
                          user: User = Depends(get_current_active_user)) -> models.VCSSubprocess:
    return impl.edit_subprocess(subprocess_id, project_id, user.id, vcs_post)


@router.delete(
    '/project/{project_id}/subprocess/{subprocess_id}/delete',
    summary='Deletes a subprocess',
    response_model=bool,
)
async def delete_subprocess(subprocess_id: int, project_id: int,
                            user: User = Depends(get_current_active_user)) -> bool:
    return impl.delete_subprocess(subprocess_id, project_id, user.id)


@router.put(
    '/project/{project_id}/subprocess/update-indices',
    summary='Updates the indices of multiple subprocesses',
    response_model=bool,
)
async def update_indices_subprocess(subprocess_ids: List[int], order_indices: List[int], project_id: int,
                                    user: User = Depends(get_current_active_user)) -> bool:
    return impl.update_indices_subprocess(subprocess_ids, order_indices, project_id, user.id)


# ======================================================================================================================
# VCS Table
# ======================================================================================================================

@router.get(
    '/project/{project_id}/vcs/{vcs_id}/get/table',
    summary='Returns the table of a a VCS',
    response_model=models.TableGet,
)
async def get_vcs_table(vcs_id: int, project_id: int, user: User = Depends(get_current_active_user)) -> models.TableGet:
    impl.get_vcs(vcs_id, project_id, user.id)  # perfoming necessary controls
    return impl.get_vcs_table(vcs_id, project_id, user.id)


@router.post(
    '/project/{project_id}/vcs/{vcs_id}/create/table',
    summary='Creates the table for a VCS',
    response_model=bool,
)
async def create_vcs_table(new_table: models.TablePost, vcs_id: int, project_id: int,
                           user: User = Depends(get_current_active_user)) -> bool:
    impl.get_vcs(vcs_id, project_id, user.id)  # perfoms necessary controls
    return impl.create_vcs_table(new_table, vcs_id, project_id, user.id)


# ======================================================================================================================
# CVS Design
# ======================================================================================================================

@router.post(
    '/project/{project_id}/vcs/{vcs_id}/design/create',
    summary='Creates a Design',
    response_model=models.Design
)
async def create_design(design_post: models.DesignPost, vcs_id: int, project_id: int, user: User = Depends(get_current_active_user)) -> models.Design:
    return impl.create_cvs_design(design_post, vcs_id, project_id, user.id)


@router.get(
    '/project/{project_id}/vcs/{vcs_id}/design/get/{design_id}',
    summary='Returns a design',
    response_model=models.Design
)
async def get_design(design_id: int, vcs_id: int, project_id: int, user: User=Depends(get_current_active_user)) -> models.Design:
    return impl.get_design(design_id, vcs_id, project_id, user.id)

@router.get(
    '/project/{project_id}/vcs/{vcs_id}/design/get/all',
    summary='Returns all designs with project id={project_id} and vcs_id{vcs_id}',
    response_model=ListChunk[models.Design]
)
async def get_all_designs(project_id: int, vcs_id: int, user: User=Depends(get_current_active_user)):
    return impl.get_all_design(project_id, vcs_id, user.id)
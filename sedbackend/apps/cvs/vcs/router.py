from typing import List
from fastapi import Depends, APIRouter
from sedbackend.apps.core.authentication.utils import get_current_active_user
from sedbackend.apps.core.users.models import User
from sedbackend.libs.datastructures.pagination import ListChunk
from sedbackend.apps.cvs.vcs import models, implementation

router = APIRouter()

# ======================================================================================================================
# VCS
# ======================================================================================================================


@router.get(
    '/project/{project_id}/vcs/all',
    summary='Returns all of VCSs of a project',
    response_model=ListChunk[models.VCS],
)
async def get_all_vcs(project_id: int, user: User = Depends(get_current_active_user)) -> ListChunk[models.VCS]:
    return implementation.get_all_vcs(project_id, user.id)

'''
@router.get(
    '/project/{project_id}/vcs/get/segment',
    summary='Returns a segment of the VCSs of a project',
    response_model=ListChunk[models.VCS],
)
async def get_segment_vcs(project_id: int, index: int, segment_length: int,
                          user: User = Depends(get_current_active_user)) -> ListChunk[models.VCS]:
    return implementation.get_segment_vcs(project_id, index, segment_length, user.id)
'''

@router.get(
    '/project/{project_id}/vcs/{vcs_id}',
    summary='Returns a VCS',
    response_model=models.VCS,
)
async def get_vcs(vcs_id: int, project_id: int, user: User = Depends(get_current_active_user)) -> models.VCS:
    return implementation.get_vcs(vcs_id, project_id, user.id)


@router.post(
    '/project/{project_id}/vcs',
    summary='Creates a new VCS in a project',
    response_model=models.VCS,
)
async def create_vcs(vcs_post: models.VCSPost, project_id: int,
                     user: User = Depends(get_current_active_user)) -> models.VCS:
    return implementation.create_vcs(vcs_post, project_id, user.id)


@router.put(
    '/project/{project_id}/vcs/{vcs_id}',
    summary='Edits a VCS',
    response_model=models.VCS,
)
async def edit_vcs(vcs_id: int, project_id: int, vcs_post: models.VCSPost,
                   user: User = Depends(get_current_active_user)) -> models.VCS:
    return implementation.edit_vcs(vcs_id, project_id, user.id, vcs_post)


@router.delete(
    '/project/{project_id}/vcs/{vcs_id}',
    summary='Deletes a VCS based on id',
    response_model=bool,
)
async def delete_vcs(vcs_id: int, project_id: int, user: User = Depends(get_current_active_user)) -> bool:
    return implementation.delete_vcs(vcs_id, project_id, user.id)



# ======================================================================================================================
# VCS Table
# ======================================================================================================================


@router.get(
    '/vcs/{vcs_id}/table',
    summary='Returns the table of a a VCS',
    response_model=List[models.VcsRow],
)
async def get_vcs_table(vcs_id: int, user: User = Depends(get_current_active_user)) -> List[models.VcsRow]:
    #implementation.get_vcs(vcs_id, user.id)  # perfoming necessary controls
    return implementation.get_vcs_table(vcs_id, user.id)


@router.post(
    '/vcs/{vcs_id}/table',
    summary='Creates the table for a VCS',
    response_model=bool,
)
async def create_vcs_table(new_table: List[models.VcsRowPost], vcs_id: int) -> bool:
#    implementation.get_vcs(vcs_id, project_id, user.id)  # perfoms necessary controls
    return implementation.create_vcs_table(new_table, vcs_id)

@router.put(
    '/vcs/{vcs_id}/table',
    summary='Edits rows of the vcs table',
    response_model=bool
)
async def edit_vcs_table(updated_table: List[models.VcsRow], vcs_id: int) -> bool:
    return implementation.edit_vcs_table(updated_table, vcs_id)

@router.delete(
    '/vcs/{vcs_id}/row/{row_id}',
    summary='Deletes the specified row',
    response_model=bool
)
async def delete_vcs_row(row_id: int, vcs_id: int) -> bool:
    return implementation.delete_vcs_row(row_id, vcs_id)

# ======================================================================================================================
# VCS Value driver
# ======================================================================================================================


@router.get(
    '/vcs/{vcs_id}/value-driver/all',
    summary='Returns all of value drivers of a project that are associated with a row',
    response_model=List[models.ValueDriver],
)
async def get_all_value_driver(vcs_id: int) -> List[models.ValueDriver]:
    return implementation.get_all_value_driver(vcs_id)


@router.get(
    '/value-driver/{value_driver_id}',
    summary='Returns a value driver',
    response_model=models.ValueDriver,
)
async def get_value_driver(value_driver_id: int) -> models.ValueDriver:
    return implementation.get_value_driver(value_driver_id)


@router.post(
    '/vcs/{vcs_id}/value-driver',
    summary='Creates a new value driver in a project',
    response_model=models.ValueDriver,
)
async def create_value_driver(value_driver_post: models.ValueDriverPost, vcs_id: int) -> models.ValueDriver:
    return implementation.create_value_driver(vcs_id, value_driver_post)


@router.put(
    '/value-driver/{value_driver_id}',
    summary='Edits a value driver',
    response_model=models.ValueDriver,
)
async def edit_value_driver(value_driver_id: int, vcs_post: models.ValueDriverPost) -> models.ValueDriver:
    return implementation.edit_value_driver(value_driver_id, vcs_post)


@router.delete(
    '/value-driver/{value_driver_id}',
    summary='Deletes a value driver',
    response_model=bool,
)
async def delete_value_driver(value_driver_id: int) -> bool:
    return implementation.delete_value_driver(value_driver_id)


# ======================================================================================================================
# VCS ISO Processes
# ======================================================================================================================


@router.get(
    '/vcs/iso-processes/all',
    summary='Returns all ISO processes',
    response_model=List[models.VCSISOProcess],
)
async def get_all_iso_process() -> List[models.VCSISOProcess]:
    return implementation.get_all_iso_process()


# ======================================================================================================================
# VCS Subprocesses
# ======================================================================================================================


@router.get(
    '/vcs/{vcs_id}/subprocess/all',
    summary='Returns all subprocesses of a project',
    response_model=ListChunk[models.VCSSubprocess],
)
async def get_all_subprocess(vcs_id: int) -> List[models.VCSSubprocess]:
    return implementation.get_all_subprocess(vcs_id)


@router.get(
    '/subprocess/{subprocess_id}',
    summary='Returns a subprocess',
    response_model=models.VCSSubprocess,
)
async def get_subprocess(subprocess_id: int) -> models.VCSSubprocess:
    return implementation.get_subprocess(subprocess_id)


@router.post(
    '/vcs/{vcs_id}/subprocess',
    summary='Creates a new subprocess',
    response_model=models.VCSSubprocess,
)
async def create_subprocess(vcs_id: int, subprocess_post: models.VCSSubprocessPost) -> models.VCSSubprocess:
    return implementation.create_subprocess(vcs_id, subprocess_post)


@router.put(
    '/subprocess/{subprocess_id}',
    summary='Edits a subprocess',
    response_model=models.VCSSubprocess,
)
async def edit_subprocess(subprocess_id: int, vcs_post: models.VCSSubprocessPost) -> models.VCSSubprocess:
    return implementation.edit_subprocess(subprocess_id, vcs_post)


@router.delete(
    '/subprocess/{subprocess_id}',
    summary='Deletes a subprocess',
    response_model=bool,
)
async def delete_subprocess(subprocess_id: int) -> bool:
    return implementation.delete_subprocess(subprocess_id)


@router.put(
    '/subprocess/{subprocess_id}',
    summary='Updates the indices of multiple subprocesses',
    response_model=bool,
)
async def update_indices_subprocess(subprocess_ids: List[int], order_indices: List[int], project_id: int,
                                    user: User = Depends(get_current_active_user)) -> bool:
    return implementation.update_indices_subprocess(subprocess_ids, order_indices, project_id, user.id)


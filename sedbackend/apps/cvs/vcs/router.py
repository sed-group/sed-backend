from typing import List, Tuple
from fastapi import Depends, APIRouter
from sedbackend.apps.core.authentication.utils import get_current_active_user
from sedbackend.apps.core.projects.dependencies import SubProjectAccessChecker
from sedbackend.apps.core.projects.models import AccessLevel
from sedbackend.apps.core.users.models import User
from sedbackend.apps.cvs.project.router import CVS_APP_SID
from sedbackend.apps.cvs.vcs.models import ValueDriver
from sedbackend.libs.datastructures.pagination import ListChunk
from sedbackend.apps.cvs.vcs import models, implementation, implementation as vcs_impl

router = APIRouter()


# ======================================================================================================================
# VCS
# ======================================================================================================================


@router.get(
    '/project/{native_project_id}/vcs/all',
    summary='Returns all of VCSs of a project',
    response_model=ListChunk[models.VCS],
    dependencies=[Depends(SubProjectAccessChecker(AccessLevel.list_can_read(), CVS_APP_SID))]
)
async def get_all_vcs(native_project_id: int, user: User = Depends(get_current_active_user)) -> ListChunk[models.VCS]:
    return implementation.get_all_vcs(native_project_id, user.id)


@router.get(
    '/project/{native_project_id}/vcs/{vcs_id}',
    summary='Returns a VCS',
    response_model=models.VCS,
    dependencies=[Depends(SubProjectAccessChecker(AccessLevel.list_can_read(), CVS_APP_SID))]
)
async def get_vcs(native_project_id: int, vcs_id: int, user: User = Depends(get_current_active_user)) -> models.VCS:
    return implementation.get_vcs(native_project_id, vcs_id, user.id)


@router.post(
    '/project/{native_project_id}/vcs',
    summary='Creates a new VCS in a project',
    response_model=models.VCS,
    dependencies=[Depends(SubProjectAccessChecker(AccessLevel.list_can_edit(), CVS_APP_SID))]
)
async def create_vcs(native_project_id: int, vcs_post: models.VCSPost,
                     user: User = Depends(get_current_active_user)) -> models.VCS:
    return implementation.create_vcs(native_project_id, vcs_post, user.id)


@router.put(
    '/project/{native_project_id}/vcs/{vcs_id}',
    summary='Edits a VCS',
    response_model=models.VCS,
    dependencies=[Depends(SubProjectAccessChecker(AccessLevel.list_can_edit(), CVS_APP_SID))]
)
async def edit_vcs(native_project_id: int, vcs_id: int, vcs_post: models.VCSPost) -> models.VCS:
    return implementation.edit_vcs(native_project_id, vcs_id, vcs_post)


@router.delete(
    '/project/{native_project_id}/vcs/{vcs_id}',
    summary='Deletes a VCS based on id',
    response_model=bool,
    dependencies=[Depends(SubProjectAccessChecker(AccessLevel.list_can_edit(), CVS_APP_SID))]
)
async def delete_vcs(native_project_id: int, vcs_id: int, user: User = Depends(get_current_active_user)) -> bool:
    return implementation.delete_vcs(user.id, native_project_id, vcs_id)


# ======================================================================================================================
# VCS Table
# ======================================================================================================================


@router.get(
    '/project/{native_project_id}/vcs/{vcs_id}/table',
    summary='Returns the table of a a VCS',
    response_model=List[models.VcsRow],
    dependencies=[Depends(SubProjectAccessChecker(AccessLevel.list_can_read(), CVS_APP_SID))]
)
async def get_vcs_table(native_project_id: int, vcs_id: int) -> List[models.VcsRow]:
    return implementation.get_vcs_table(native_project_id, vcs_id)


@router.put(
    '/project/{native_project_id}/vcs/{vcs_id}/table',
    summary='Edits rows of the vcs table',
    response_model=bool,
    dependencies=[Depends(SubProjectAccessChecker(AccessLevel.list_can_edit(), CVS_APP_SID))]
)
async def edit_vcs_table(native_project_id: int, vcs_id: int, updated_table: List[models.VcsRowPost]) -> bool:
    return implementation.edit_vcs_table(native_project_id, vcs_id, updated_table)


# ======================================================================================================================
# VCS Value driver
# ======================================================================================================================


@router.get(
    '/value-driver/all',
    summary='Returns all of value drivers',
    response_model=List[models.ValueDriver],
)
async def get_all_value_driver(user: User = Depends(get_current_active_user)) -> List[models.ValueDriver]:
    return implementation.get_all_value_driver(user.id)


@router.get(
    '/project/{native_project_id}/vcs/{vcs_id}/value-driver/all',
    summary='Fetch all value drivers in a vcs',
    response_model=List[ValueDriver],
    dependencies=[Depends(SubProjectAccessChecker(AccessLevel.list_can_read(), CVS_APP_SID))]
)
async def get_all_value_driver_vcs(native_project_id: int, vcs_id: int) -> List[ValueDriver]:
    return vcs_impl.get_all_value_driver_vcs(native_project_id, vcs_id)


@router.get(
    '/project/{native_project_id}/vcs/{vcs_id}/row/{vcs_row_id}/value-driver/all',
    summary='Fetch all value drivers from a vcs row',
    response_model=List[ValueDriver],
    dependencies=[Depends(SubProjectAccessChecker(AccessLevel.list_can_read(), CVS_APP_SID))]
)
async def get_value_drivers_vcs_row(native_project_id: int, vcs_id: int, vcs_row_id: int,
                                    user: User = Depends(get_current_active_user)) -> List[ValueDriver]:
    return vcs_impl.get_all_value_drivers_vcs_row(native_project_id, vcs_id, vcs_row_id, user.id)


@router.get(
    '/value-driver/{value_driver_id}',
    summary='Returns a value driver',
    response_model=models.ValueDriver,
)
async def get_value_driver(value_driver_id: int, user: User = Depends(get_current_active_user)) -> models.ValueDriver:
    return implementation.get_value_driver(value_driver_id, user.id)


@router.post(
    '/value-driver',
    summary='Creates a new value driver',
    response_model=models.ValueDriver,
)
async def create_value_driver(value_driver_post: models.ValueDriverPost,
                              user: User = Depends(get_current_active_user)) -> models.ValueDriver:
    return implementation.create_value_driver(user.id, value_driver_post)

@router.post(
    '/project/{native_project_id}/value-driver',
    summary=f'Add value drivers to project',
    response_model=bool,
    dependencies=[Depends(SubProjectAccessChecker(AccessLevel.list_can_edit(), CVS_APP_SID))]
)
async def add_drivers_to_project(native_project_id: int, value_driver_ids: List[int]):
    return implementation.add_project_multiple_value_drivers(native_project_id, value_driver_ids)

@router.post(
    '/project/{native_project_id}/value-driver/need',
    summary=f'Add value drivers to stakeholder needs',
    response_model=bool,
    dependencies=[Depends(SubProjectAccessChecker(AccessLevel.list_can_edit(), CVS_APP_SID))]
)
async def add_drivers_to_needs(native_project_id: int, need_driver_ids: List[Tuple[int, int]]):
    return implementation.add_vcs_multiple_needs_drivers(need_driver_ids)

@router.put(
    '/value-driver/{value_driver_id}',
    summary='Edits a value driver',
    response_model=models.ValueDriver,
)
async def edit_value_driver(value_driver_id: int, value_driver: models.ValueDriverPut,
                            user: User = Depends(get_current_active_user)) -> models.ValueDriver:
    return implementation.edit_value_driver(value_driver_id, value_driver, user.id)


@router.delete(
    '/project/{native_project_id}/value-driver/{value_driver_id}',
    summary='Deletes a value driver',
    response_model=bool,
)
async def delete_value_driver(native_project_id: int, value_driver_id: int) -> bool:
    return implementation.delete_value_driver(native_project_id, value_driver_id)


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
    '/project/{native_project_id}/subprocess/all',
    summary='Returns all subprocesses of a project',
    response_model=List[models.VCSSubprocess],
    dependencies=[Depends(SubProjectAccessChecker(AccessLevel.list_can_read(), CVS_APP_SID))]
)
async def get_all_subprocess(native_project_id: int) -> List[models.VCSSubprocess]:
    return implementation.get_all_subprocess(native_project_id)


@router.get(
    '/project/{native_project_id}/subprocess/{subprocess_id}',
    summary='Returns a subprocess',
    response_model=models.VCSSubprocess,
    dependencies=[Depends(SubProjectAccessChecker(AccessLevel.list_can_read(), CVS_APP_SID))]
)
async def get_subprocess(native_project_id: int, subprocess_id: int) -> models.VCSSubprocess:
    return implementation.get_subprocess(native_project_id, subprocess_id)


@router.post(
    '/project/{native_project_id}/subprocess',
    summary='Creates a new subprocess',
    response_model=models.VCSSubprocess,
    dependencies=[Depends(SubProjectAccessChecker(AccessLevel.list_can_edit(), CVS_APP_SID))]
)
async def create_subprocess(native_project_id: int,
                            subprocess_post: models.VCSSubprocessPost) -> models.VCSSubprocess:
    return implementation.create_subprocess(native_project_id, subprocess_post)


@router.put(
    '/project/{native_project_id}/subprocess/{subprocess_id}',
    summary='Edits a subprocess',
    response_model=bool,
    dependencies=[Depends(SubProjectAccessChecker(AccessLevel.list_can_edit(), CVS_APP_SID))]
)
async def edit_subprocess(native_project_id: int, subprocess_id: int,
                          subprocess: models.VCSSubprocessPut) -> bool:
    return implementation.edit_subprocess(native_project_id, subprocess_id, subprocess)


@router.delete(
    '/project/{native_project_id}/subprocess/{subprocess_id}',
    summary='Deletes a subprocess',
    response_model=bool,
    dependencies=[Depends(SubProjectAccessChecker(AccessLevel.list_can_edit(), CVS_APP_SID))]
)
async def delete_subprocess(native_project_id: int, subprocess_id: int) -> bool:
    return implementation.delete_subprocess(native_project_id, subprocess_id)


# ======================================================================================================================
# VCS Duplicate
# ======================================================================================================================

@router.post(
    '/project/{native_project_id}/vcs/{vcs_id}/duplicate/{n}',
    summary='Duplicate VCS n times',
    response_model=List[models.VCS],
    dependencies=[Depends(SubProjectAccessChecker(AccessLevel.list_can_edit(), CVS_APP_SID))]
)
async def duplicate_vcs(native_project_id: int, vcs_id: int, n: int, user: User = Depends(get_current_active_user)) -> List[models.VCS]:
    return implementation.duplicate_vcs(native_project_id, vcs_id, n, user.id)

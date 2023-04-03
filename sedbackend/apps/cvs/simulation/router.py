from operator import mod
from fastapi import Depends, APIRouter, UploadFile, File, HTTPException

from typing import List, Optional
from sedbackend.apps.core.authentication.utils import get_current_active_user
from sedbackend.apps.core.projects.dependencies import SubProjectAccessChecker
from sedbackend.apps.core.projects.models import AccessLevel
from sedbackend.apps.cvs.project.router import CVS_APP_SID
from sedbackend.apps.core.users.models import User
from sedbackend.apps.cvs.simulation import implementation, models

router = APIRouter()


@router.post(
    '/project/{native_project_id}/simulation/run',
    summary='Run simulation',
    response_model=List[models.Simulation],
    dependencies=[Depends(SubProjectAccessChecker(AccessLevel.list_can_read, CVS_APP_SID))]
)
async def run_simulation(native_project_id: int, sim_settings: models.EditSimSettings, vcs_ids: List[int],
                         design_group_ids: List[int],
                         normalized_npv: Optional[bool] = False,
                         user: User = Depends(get_current_active_user)) -> List[models.Simulation]:
    return implementation.run_simulation(native_project_id, sim_settings, vcs_ids, design_group_ids, normalized_npv,
                                         user.id)


@router.post(
    '/project/{native_project_id}/sim/upload-dsm',
    summary='Run simulation with DSM predefined in Excel or CSV file',
    response_model=List[models.Simulation],
    dependencies=[Depends(SubProjectAccessChecker(AccessLevel.list_can_read, CVS_APP_SID))]
)
async def run_dsm_file_simulation(native_project_id: int, sim_params: models.FileParams = Depends(),
                                  dsm_file: UploadFile = File(default=None),
                                  user: User = Depends(get_current_active_user)) -> List[models.Simulation]:
    if dsm_file.content_type != 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' and \
            dsm_file.content_type != 'text/csv':
        print("Content-type: ", dsm_file.content_type)
        raise HTTPException(400, detail="Invalid file type")
    return implementation.run_dsm_file_simulation(user.id, native_project_id, sim_params, dsm_file)


@router.post(
    '/project/{native_project_id}/simulation/run-multiprocessing',
    summary='Run monte carlo simulation with multiprocessing',
    response_model=List[models.Simulation],
    dependencies=[Depends(SubProjectAccessChecker(AccessLevel.list_can_read, CVS_APP_SID))]
)
async def run_sim_monte_carlo(native_project_id: int, sim_settings: models.EditSimSettings, vcs_ids: List[int],
                              design_group_ids: List[int],
                              normalized_npv: Optional[bool] = False,
                              user: User = Depends(get_current_active_user)) -> List[models.Simulation]:
    return implementation.run_sim_monte_carlo(native_project_id, sim_settings, vcs_ids,
                                              design_group_ids, normalized_npv, user.id)


@router.get(
    '/project/{native_project_id}/simulation/settings',
    summary='Get settings for project',
    response_model=models.SimSettings,
    dependencies=[Depends(SubProjectAccessChecker(AccessLevel.list_can_read, CVS_APP_SID))]
)
async def get_sim_settings(native_project_id: int) -> models.SimSettings:
    return implementation.get_sim_settings(native_project_id)


@router.put(
    '/project/{native_project_id}/simulation/settings',
    summary='Create or update simulation settings',
    response_model=bool,
    dependencies=[Depends(SubProjectAccessChecker(AccessLevel.list_can_edit, CVS_APP_SID))]
)
async def put_sim_settings(native_project_id: int, sim_settings: models.EditSimSettings) -> bool:
    return implementation.edit_sim_settings(native_project_id, sim_settings)

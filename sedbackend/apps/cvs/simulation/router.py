from operator import mod
from fastapi import Depends, APIRouter, UploadFile, File

from typing import List, Optional
from sedbackend.apps.core.authentication.utils import get_current_active_user
from sedbackend.apps.core.users.models import User
from sedbackend.apps.cvs.simulation import implementation, models

router = APIRouter()


@router.get(
    '/project/{project_id}/simulation/run',
    summary='Run simulation',
    response_model=models.Simulation,
)
async def run_simulation(project_id: int, vcs_ids: List[int], design_ids: Optional[List[int]] = None, 
                        normalized_npv: Optional[bool] = False, 
                        user: User = Depends(get_current_active_user)) -> models.Simulation:
    return implementation.run_simulation(project_id, vcs_ids, design_ids, normalized_npv, user.id)

@router.post(
    '/project/vcs/{vcs_id}/sim/csv',
    summary='Run simulation with DSM predefined in CSV file',
    response_model=models.Simulation,
)
async def run_csv_simulation(vcs_id: int, flow_time: float, flow_rate: float, flow_process_id: int, 
                        simulation_runtime: float, discount_rate: float, non_tech_add: models.NonTechCost,
                        dsm_csv: UploadFile = File(default=None), design_ids: Optional[List[int]] = None, 
                        normalized_npv: Optional[bool] = False, 
                        user: User = Depends(get_current_active_user)) -> models.Simulation:
    return implementation.run_csv_simulation(vcs_id, flow_time, flow_rate, flow_process_id, simulation_runtime, 
                                            discount_rate, non_tech_add, dsm_csv, design_ids, normalized_npv, user.id)


@router.post(
    '/project/vcs/{vcs_id}/sim/excel',
    summary='Run simulation with DSM predefined in Excel file',
    response_model=models.Simulation,
)
async def run_xlsx_simulation(vcs_id: int, flow_time: float, flow_rate: float, flow_process_id: int, 
                            simulation_runtime: float, discount_rate: float, non_tech_add: models.NonTechCost,
                            dsm_xlsx: UploadFile = File(default=None), design_ids: Optional[List[int]] = None, 
                            normalized_npv: Optional[bool] = False,  
                            user: User = Depends(get_current_active_user)) -> models.Simulation:
    return implementation.run_xlsx_simulation(vcs_id, flow_time, flow_rate, flow_process_id, simulation_runtime, 
                                                discount_rate, non_tech_add, dsm_xlsx, design_ids, normalized_npv, user.id)

@router.post(
    '/project/{project_id}/simulation/run-multiprocessing',
    summary='Run monte carlo simulation with multiprocessing',
    response_model=List[models.SimulationMonteCarlo],
)
async def run_sim_monte_carlo(project_id: int, vcs_ids: List[int], design_ids: Optional[List[int]] = None, 
                        normalized_npv: Optional[bool] = False,
                        user: User = Depends(get_current_active_user)) -> models.SimulationMonteCarlo:
    return implementation.run_sim_monte_carlo(project_id, vcs_ids,
                                            design_ids, normalized_npv, user.id)

@router.get(
    '/project/{project_id}/simulation/settings',
    summary='Get settings for project',
    response_model=models.SimSettings
)
async def get_sim_settings(project_id: int) -> models.SimSettings:
    return implementation.get_sim_settings(project_id)

@router.put(
    '/project/{project_id}/simulation/settings',
    summary='Create or update simulation settings',
    response_model=bool
)
async def put_sim_settings(project_id: int, sim_settings: models.EditSimSettings) -> bool:
    return implementation.edit_sim_settings(project_id, sim_settings)
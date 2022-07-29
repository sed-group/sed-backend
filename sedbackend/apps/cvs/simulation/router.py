from fastapi import Depends, APIRouter, UploadFile, File

from sedbackend.apps.core.authentication.utils import get_current_active_user
from sedbackend.apps.core.users.models import User
from sedbackend.apps.cvs.simulation import implementation, models

router = APIRouter()


@router.get(
    '/project/vcs/{vcs_id}/simulation/run',
    summary='Run simulation',
    response_model=models.Simulation,
)
async def run_simulation(project_id: int, vcs_id: int, flow_time: float,
                        flow_rate: float, flow_process_id: int, simulation_runtime: float,
                        discount_rate: float, user: User = Depends(get_current_active_user)) -> models.Simulation:
    return implementation.run_simulation(project_id, vcs_id, flow_time, flow_rate, flow_process_id, 
                                            simulation_runtime, discount_rate, user.id)

@router.post(
    '/project/vcs/{vcs_id}/sim/csv',
    summary='Run simulation with DSM predefined in CSV file',
    response_model=models.Simulation,
)
async def run_csv_simulation(project_id: int, vcs_id: int, flow_time: float, flow_rate: float, 
                        flow_process_id: int, simulation_runtime: float, discount_rate: float, 
                        dsm_csv: UploadFile = File(default=None), user: User = Depends(get_current_active_user)) -> models.Simulation:
    return implementation.run_csv_simulation(project_id, vcs_id, flow_time, flow_rate, flow_process_id, 
                                            simulation_runtime, discount_rate, dsm_csv, user.id)


@router.post(
    '/project/vcs/{vcs_id}/sim/excel',
    summary='Run simulation with DSM predefined in Excel file',
    response_model=models.Simulation,
)
async def run_xlsx_simulation(project_id: int, vcs_id: int, flow_time: float, flow_rate: float, 
                        flow_process_id: int, simulation_runtime: float, discount_rate: float, 
                        dsm_xlsx: UploadFile = File(default=None), user: User = Depends(get_current_active_user)) -> models.Simulation:
    return implementation.run_xlsx_simulation(project_id, vcs_id, flow_time, flow_rate, flow_process_id, 
                                            simulation_runtime, discount_rate, dsm_xlsx, user.id)

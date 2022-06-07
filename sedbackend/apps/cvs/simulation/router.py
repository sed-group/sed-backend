from fastapi import Depends, APIRouter

from sedbackend.apps.core.authentication.utils import get_current_active_user
from sedbackend.apps.core.users.models import User
from sedbackend.apps.cvs.simulation import implementation, models

router = APIRouter()


@router.get(
    '/project/{project_id}/vcs/{vcs_id}/simulation/run',
    summary='Run simulation',
    response_model=models.Simulation,
)
async def run_simulation(project_id: int, vcs_id: int, time_interval: float,
                         user: User = Depends(get_current_active_user)) -> models.Simulation:
    return implementation.run_simulation(project_id, vcs_id, time_interval, user.id)
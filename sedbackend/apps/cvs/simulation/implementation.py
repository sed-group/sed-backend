from fastapi import HTTPException
from starlette import status

import sedbackend.apps
from sedbackend.apps.cvs.simulation import models, algorithms

from sedbackend.apps.core.authentication import exceptions as auth_ex
from sedbackend.apps.core.db import get_connection
from sedbackend.apps.cvs.project import exceptions as project_exceptions
from sedbackend.apps.cvs.simulation.exceptions import ProcessNotFoundException
from sedbackend.apps.cvs.vcs import exceptions as vcs_exceptions
from sedbackend.apps.cvs.market_input import exceptions as market_input_exceptions


def run_simulation(project_id: int, vcs_id: int, flow_time: float, flow_rate: float, 
                    flow_process_id: int, simulation_runtime: float, discount_rate: float, 
                    user_id: int) -> models.Simulation:
    try:
        with get_connection() as con:
            result = algorithms.run_simulation(con,project_id, vcs_id, flow_time, flow_rate, 
                                                    flow_process_id, simulation_runtime, discount_rate, user_id)
            return result
    except auth_ex.UnauthorizedOperationException:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Unauthorized user.',
        )
    except vcs_exceptions.VCSNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Could not find vcs with id={vcs_id}.',
        )
    except project_exceptions.CVSProjectNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Could not find project with id={project_id}.',
        )
    except market_input_exceptions.MarketInputNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Could not find market input',
        )
    except ProcessNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Could not find process',
        )

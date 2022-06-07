from fastapi import HTTPException
from starlette import status

import sedbackend.apps
import sedbackend.apps.cvs.simulation.algorithms
from sedbackend.apps.core.authentication import exceptions as auth_ex
from sedbackend.apps.core.db import get_connection
from sedbackend.apps.cvs.project import exceptions as project_exceptions
from sedbackend.apps.cvs.vcs import exceptions as vcs_exceptions
from sedbackend.apps.cvs.market_input import exceptions as market_input_exceptions


def run_simulation(project_id: int, vcs_id: int, time_interval: float, user_id: int) -> \
        sedbackend.apps.cvs.simulation.algorithms.Simulation:
    try:
        with get_connection() as con:
            result = sedbackend.apps.cvs.simulation.algorithms.run_simulation(con, project_id, vcs_id, user_id,
                                                                              time_interval)
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

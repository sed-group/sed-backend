from fastapi import HTTPException, UploadFile
from starlette import status
import tempfile

from sedbackend.apps.cvs.life_cycle import storage
from sedbackend.apps.cvs.simulation import models, algorithms, storage

from sedbackend.apps.core.authentication import exceptions as auth_ex
from sedbackend.apps.core.db import get_connection
from sedbackend.apps.cvs.project import exceptions as project_exceptions
from sedbackend.apps.cvs.simulation.exceptions import DSMFileNotFoundException, ProcessNotFoundException
from sedbackend.apps.cvs.vcs import exceptions as vcs_exceptions
from sedbackend.apps.cvs.market_input import exceptions as market_input_exceptions


def run_simulation(vcs_id: int, flow_time: float, flow_rate: float, 
                    flow_process_id: int, simulation_runtime: float, discount_rate: float, 
                    non_tech_add: str, user_id: int) -> models.Simulation:
    try:
        with get_connection() as con:
            result = storage.run_simulation(con, vcs_id, flow_time, flow_rate, flow_process_id, 
                                simulation_runtime, discount_rate, non_tech_add, user_id)
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
            detail=f'Could not find project.',
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


def run_csv_simulation(vcs_id: int, flow_time: float, flow_rate: float, 
                        flow_process_id: int, simulation_runtime: float, discount_rate: float, 
                        non_tech_add: str, dsm_csv: UploadFile, user_id: int) -> models.Simulation:
    try: 
        with get_connection() as con:
            res = storage.run_sim_with_csv_dsm(con, vcs_id, flow_time, flow_rate, flow_process_id, 
                                simulation_runtime, discount_rate, non_tech_add, dsm_csv, user_id)
            return res
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
            detail=f'Could not find project.',
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
    except DSMFileNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Could not read uploaded file'
        )

def run_xlsx_simulation(vcs_id: int, flow_time: float, flow_rate: float, flow_process_id: int, 
                        simulation_runtime: float, discount_rate: float, non_tech_add: str, 
                        dsm_xlsx: UploadFile, user_id: int) -> models.Simulation:
    try: 
        with get_connection() as con:
            res = storage.run_sim_with_xlsx_dsm(con, vcs_id, flow_time, flow_rate, flow_process_id, 
                            simulation_runtime, discount_rate, non_tech_add, dsm_xlsx, user_id)
            return res
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
            detail=f'Could not find project.',
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
    except DSMFileNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Could not read uploaded file'
        )

def run_sim_mp(vcs_id: int, flow_time: float, flow_rate: float, 
                    flow_process_id: int, simulation_runtime: float, discount_rate: float, 
                    non_tech_add: str, user_id: int) -> models.Simulation:
    try: 
        with get_connection() as con:
            result = storage.run_sim_mp(con, vcs_id, flow_time, flow_rate, flow_process_id, 
                                simulation_runtime, discount_rate, non_tech_add, user_id)
            return result
    except vcs_exceptions.GenericDatabaseException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Fel'
        )

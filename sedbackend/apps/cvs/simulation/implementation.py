from fastapi import HTTPException, UploadFile
from starlette import status
import tempfile

from typing import List, Optional

from fastapi.logger import logger
from sedbackend.apps.cvs.simulation import models, storage

from sedbackend.apps.core.authentication import exceptions as auth_ex
from sedbackend.apps.core.db import get_connection
from sedbackend.apps.cvs.project import exceptions as project_exceptions
from sedbackend.apps.cvs.simulation.exceptions import DSMFileNotFoundException, DesignIdsNotFoundException, FormulaEvalException, NegativeTimeException, ProcessNotFoundException, RateWrongOrderException, InvalidFlowSettingsException
from sedbackend.apps.cvs.vcs import exceptions as vcs_exceptions
from sedbackend.apps.cvs.market_input import exceptions as market_input_exceptions


def run_simulation(project_id: int, sim_settings: models.EditSimSettings, vcs_ids: List[int], design_ids: List[int], 
                    normalized_npv: bool, user_id: int) -> List[models.Simulation]:
    try:
        with get_connection() as con:
            result = storage.run_simulation(con, project_id, sim_settings, vcs_ids, design_ids, normalized_npv, user_id)
            return result
    except auth_ex.UnauthorizedOperationException:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Unauthorized user.',
        )
    except vcs_exceptions.VCSNotFoundException: #This exception will probably never fire
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Could not find vcs.',
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
    except FormulaEvalException as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'Could not evaluate formulas of process with id: {e.process_id}'
        )
    except RateWrongOrderException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Wrong order of rate of entities. Per project assigned after per product'
        )
    except NegativeTimeException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Formula at process with id: {e.process_id} evaluated to negative time'
        )
    except DesignIdsNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'No design ids or empty array supplied'
        )


def run_csv_simulation(project_id: int, sim_settings: models.EditSimSettings, vcs_ids: List[int], dsm_csv: UploadFile, design_ids: List[int], 
                        normalized_npv: bool, user_id: int) -> List[models.Simulation]:
    try: 
        with get_connection() as con:
            res = storage.run_sim_with_csv_dsm(con, project_id, sim_settings, vcs_ids, dsm_csv, design_ids, 
                                normalized_npv, user_id)
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
    except FormulaEvalException as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'Could not evaluate formulas of process with id: {e.process_id}'
        )
    except RateWrongOrderException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Wrong order of rate of entities. Per project assigned after per product'
        )
    except NegativeTimeException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Formula at process with id: {e.process_id} evaluated to negative time'
        )
    except DesignIdsNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'No design ids or empty array supplied'
        )

def run_xlsx_simulation(project_id: int, sim_settings: models.EditSimSettings, vcs_ids: List[int],  design_ids: List[int], normalized_npv: bool, 
                        user_id: int) -> List[models.Simulation]:
    try: 
        with get_connection() as con:
            res = storage.run_sim_with_xlsx_dsm(con, project_id, sim_settings, vcs_ids, design_ids, normalized_npv, user_id) #Wtf saknar xlsx file
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
    except FormulaEvalException as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'Could not evaluate formulas of process with id: {e.process_id}'
        )
    except RateWrongOrderException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Wrong order of rate of entities. Per project assigned after per product'
        )
    except NegativeTimeException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Formula at process with id: {e.process_id} evaluated to negative time'
        )
    except DesignIdsNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'No design ids or empty array supplied'
        )

def run_sim_monte_carlo(project_id: int, sim_settings: models.EditSimSettings, vcs_ids: List[int], design_ids: List[int], 
        normalized_npv: bool, user_id: int = None) -> List[models.Simulation]:
    try: 
        with get_connection() as con:
            result = storage.run_sim_monte_carlo(con, project_id, sim_settings, vcs_ids,  
                                        design_ids, normalized_npv, user_id)
            return result
    except vcs_exceptions.GenericDatabaseException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Fel'
        )
    except FormulaEvalException as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'Could not evaluate formulas of process with id: {e.process_id}'
        )
    except RateWrongOrderException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Wrong order of rate of entities. Per project assigned after per product'
        )
    except NegativeTimeException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Formula at process with id: {e.process_id} evaluated to negative time'
        )
    except DesignIdsNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'No design ids or empty array supplied'
        )

def get_sim_settings(project_id: int) -> models.SimSettings:
    try:
        with get_connection() as con: 
            result = storage.get_simulation_settings(con, project_id)
            con.commit()
            return result
    except Exception as e:
        logger.debug(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'Could not send simulation settings'
        )

def edit_sim_settings(project_id: int, sim_settings: models.EditSimSettings) -> bool:
    try: 
        with get_connection() as con:
            res = storage.edit_simulation_settings(con, project_id, sim_settings)
            con.commit()
            return res
    except InvalidFlowSettingsException:
        logger.debug("Invalid flow settings")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Both flow process and flow start time supplied or neither supplied'
        )
    except Exception as e:
        logger.debug(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'Could not update simulation settings'
        )

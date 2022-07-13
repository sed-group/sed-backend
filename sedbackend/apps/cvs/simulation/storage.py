from fastapi import UploadFile
from mysql.connector.pooling import PooledMySQLConnection

from sedbackend.apps.cvs.simulation import models
from sedbackend.apps.cvs.simulation.algorithms import run_simulation


def run_sim_with_csv_dsm(db_connection: PooledMySQLConnection, project_id: int, vcs_id: int, flow_time: float,
                flow_rate: float, process_id: int, simulation_runtime: float, discount_rate: float, 
                dsm_csv: UploadFile, user_id: int) -> models.Simulation:
    

    return run_simulation(db_connection, project_id, vcs_id, flow_time, flow_rate, process_id, simulation_runtime, discount_rate, user_id)
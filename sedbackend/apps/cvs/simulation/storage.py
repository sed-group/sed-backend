import tempfile
from multiprocessing import Pool
from fastapi import UploadFile
from mysql.connector.pooling import PooledMySQLConnection
import pandas as pd

from typing import List

from sedbackend.apps.cvs.simulation import models
from sedbackend.apps.cvs.simulation.algorithms import *
from sedbackend.apps.cvs.market_input.models import MarketInputGet
import sedbackend.apps.cvs.simulation.exceptions as e
import sedbackend.apps.cvs.vcs.implementation as vcs_impl
import sedbackend.apps.cvs.market_input.implementation as mi_impl
import sedbackend.apps.cvs.life_cycle.implementation as lifecycle_impl
from sedbackend.apps.cvs.vcs.models import VcsRow

def run_sim_with_csv_dsm(db_connection: PooledMySQLConnection, project_id: int, vcs_id: int, flow_time: float,
                flow_rate: float, process_id: int, simulation_runtime: float, discount_rate: float, 
                dsm_csv: UploadFile, user_id: int) -> models.Simulation:

    try:
        tmp_csv = tempfile.TemporaryFile()  #Workaround because current python version doesn't support 
        tmp_csv.write(dsm_csv.file.read())      #readable() attribute on SpooledTemporaryFile which UploadFile 
        tmp_csv.seek(0)                     #is an alias for. PR is accepted for python v3.12, see https://github.com/python/cpython/pull/29560
        if dsm_csv is None:
            raise e.DSMFileNotFoundException

        dsm = get_dsm_from_csv(tmp_csv) #This should hopefully open up the file for the processor. 
        if dsm is None:
            raise e.DSMFileNotFoundException
    finally:
        tmp_csv.close()

    res = get_sim_data(db_connection, vcs_id)
    processes = []
    
    #flow_process = None
    print(dsm.keys())
    for key in dsm.keys():
        p = None
        for r in res:
            if r['iso_name'] is not None and r['sub_name'] is None:
                if key == r['iso_name']:
                    p = Process(r['time'], r['cost'], r['revenue'], r['iso_name'], TimeFormat.YEAR)
                    processes.append(p)
                    if r['id'] == process_id:
                        flow_process = p

                    break
            elif r['iso_name'] is None and r['sub_name'] is not None:
                if key == r['sub_name']:
                    p = Process(r['time'], r['cost'], r['revenue'], r['sub_name'], TimeFormat.YEAR)
                    processes.append(p)
                    if r['id'] == process_id:
                        flow_process = p
                    break
            else:
                raise e.ProcessNotFoundException
            #if r['id'] == process_id:
             #   flow_process = p
        
    
    
        
        print([p.name for p in processes])

    print(flow_process.name)        
    
    non_tech_processes = [] #TODO fix the non-tech-processes

    sim = Simulation(flow_time, flow_rate, flow_process, simulation_runtime, discount_rate, processes, non_tech_processes, dsm)
    sim.run_simulation()

    return models.Simulation(
        time=sim.time_steps,
        cumulative_NPV = sim.cum_NPV,
        processes=[models.Process(name=p.name, time=p.time, cost=p.cost, revenue=p.revenue) for p in sim.processes]
    )

def run_sim_with_xlsx_dsm(db_connection: PooledMySQLConnection, project_id: int, vcs_id: int, flow_time: float,
                flow_rate: float, process_id: int, simulation_runtime: float, discount_rate: float, 
                dsm_xlsx: UploadFile, user_id: int) -> models.Simulation:

    try:
        tmp_xlsx = tempfile.TemporaryFile()  #Workaround because current python version doesn't support 
        tmp_xlsx.write(dsm_xlsx.file.read()) #readable() attribute on SpooledTemporaryFile which UploadFile 
        tmp_xlsx.seek(0)                     #is an alias for. PR is accepted for python v3.12, see https://github.com/python/cpython/pull/29560
        if dsm_xlsx is None:
            raise e.DSMFileNotFoundException

        dsm = get_dsm_from_excel(tmp_xlsx) #This should hopefully open up the file for the processor. 
        if dsm is None:
            raise e.DSMFileNotFoundException
    finally:
        tmp_xlsx.close()

    res = get_sim_data(db_connection, vcs_id)
    processes = []
    
    for key in dsm.keys():
        for r in res:
            if r['iso_name'] is not None and r['sub_name'] is None:
                if key == r['iso_name']:
                    p = Process(r['time'], r['cost'], r['revenue'], r['iso_name'], TimeFormat.YEAR)
                    processes.append(p)
                    if r['id'] == process_id:
                        flow_process = p
                    break
            elif r['iso_name'] is None and r['sub_name'] is not None:
                if key == r['sub_name']:
                    p = Process(r['time'], r['cost'], r['revenue'], r['sub_name'], TimeFormat.YEAR)
                    processes.append(p)
                    if r['id'] == process_id:
                        flow_process = p
                    break
            else:
                raise e.ProcessNotFoundException
            
            
    
    non_tech_processes = [] #TODO fix the non-tech-processes

    sim = Simulation(flow_time, flow_rate, flow_process, simulation_runtime, discount_rate, processes, non_tech_processes, dsm)
    sim.run_simulation()

    return models.Simulation(
        time=sim.time_steps,
        cumulative_NPV = sim.cum_NPV,
        processes=[models.Process(name=p.name, time=p.time, cost=p.cost, revenue=p.revenue) for p in sim.processes]
    )
    

def get_sim_data(db_connection: PooledMySQLConnection, vcs_id: int):
    query = f'SELECT cvs_vcs_rows.id, cvs_vcs_rows.iso_process, cvs_iso_processes.name as iso_name, category, \
            subprocess, cvs_subprocesses.name as sub_name, time, cost, revenue FROM cvs_vcs_rows \
            LEFT OUTER JOIN cvs_iso_processes ON cvs_vcs_rows.iso_process = cvs_iso_processes.id \
            LEFT OUTER JOIN cvs_subprocesses ON cvs_vcs_rows.subprocess = cvs_subprocesses.id \
            LEFT OUTER JOIN cvs_market_input ON cvs_vcs_rows.id = cvs_market_input.vcs_row \
            WHERE cvs_vcs_rows.vcs = %s ORDER BY `index`'
    with db_connection.cursor(prepared=True) as cursor:
        cursor.execute(query, [vcs_id])
        res = cursor.fetchall()
        res = [dict(zip(cursor.column_names, row)) for row in res]
    return res

def run_simulation(db_connection: PooledMySQLConnection, project_id: int, vcs_id: int, flow_time: float, 
        flow_rate: float, process_id: int, simulation_runtime: float, discount_rate: float,
        user_id: int) -> models.Simulation:
    
    res = get_sim_data(db_connection, vcs_id)

    
    processes = []
    non_tech_processes = []
    for row in res:
        if row['iso_name'] is not None and row['sub_name'] is None:
            if row['category'] != 'Technical processes':
                non_tech_processes.append(Process(row['time'], row['cost'], row['revenue'], row['iso_name'], TimeFormat.YEAR))
            else:
                p = Process(row['time'], row['cost'], row['revenue'], row['iso_name'], TimeFormat.YEAR)
                processes.append(p)
                if row['id'] == process_id:
                    flow_process = p     
        elif row['iso_name'] is None and row['sub_name'] is not None:
            p = Process(row['time'], row['cost'], row['revenue'], row['sub_name'], TimeFormat.YEAR)
            processes.append(p)
            if row['id'] == process_id:
                flow_process = p
        else:
            raise e.ProcessNotFoundException

    dsm = create_simple_dsm(processes) #TODO Change to using BPMN

    sim = Simulation(flow_time, flow_rate, flow_process, simulation_runtime, discount_rate, processes, non_tech_processes, dsm)
    sim.run_simulation()

    return models.Simulation(
        time=sim.time_steps,
        cumulative_NPV=sim.cum_NPV,
        processes=[models.Process(name=p.name, time=p.time, cost=p.cost, revenue=p.revenue) for p in sim.processes]
    )

#TODO Change dsm creation to follow BPMN and the nodes in the BPMN. 
#Currently the DSM only goes from one process to the other following the order of the index in the VCS
def create_simple_dsm(processes: List[Process]) -> dict:
    l = len(processes)

    index_list = list(range(0, l))
    dsm = dict()
    for i, p in enumerate(processes):
        dsm.update({p.name: [1 if i + 1 == j else 0 for j in index_list]})

    print(dsm)
    return dsm


def get_dsm_from_csv(path):
    pf = pd.read_csv(path)

    dsm = dict()
    for v in pf.values:
        dsm.update({v[0]: v[1::].tolist()})
    return dsm

def get_dsm_from_excel(path):
    pf = pd.read_excel(path)

    dsm = dict()
    for v in pf.values:
        dsm.update({v[0]: v[1::].tolist()})
    return dsm
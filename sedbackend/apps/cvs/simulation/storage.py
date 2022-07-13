import imp
from fastapi import UploadFile
from mysql.connector.pooling import PooledMySQLConnection
import pandas as pd

from typing import List

from sedbackend.apps.cvs.simulation import models
from sedbackend.apps.cvs.simulation.algorithms import *
from sedbackend.apps.cvs.market_input.models import MarketInputGet
from sedbackend.apps.cvs.simulation.exceptions import ProcessNotFoundException
import sedbackend.apps.cvs.vcs.implementation as vcs_impl
import sedbackend.apps.cvs.market_input.implementation as mi_impl
import sedbackend.apps.cvs.life_cycle.implementation as lifecycle_impl
from sedbackend.apps.cvs.vcs.models import VcsRow

def run_sim_with_csv_dsm(db_connection: PooledMySQLConnection, project_id: int, vcs_id: int, flow_time: float,
                flow_rate: float, process_id: int, simulation_runtime: float, discount_rate: float, 
                dsm_csv: UploadFile, user_id: int) -> models.Simulation:
    

    return run_simulation(db_connection, project_id, vcs_id, flow_time, flow_rate, process_id, simulation_runtime, discount_rate, user_id)



def run_simulation(db_connection: PooledMySQLConnection, project_id: int, vcs_id: int, flow_time: float, 
        flow_rate: float, process_id: int, simulation_runtime: float, discount_rate: float,
        user_id: int) -> models.Simulation:
    
    #pid is a processid which means that we need to fetch the processes first. 
    vcs_rows = vcs_impl.get_vcs_table(vcs_id)
    market_input = mi_impl.get_all_market_inputs(project_id, vcs_id, user_id)

    flow_process = None #Should be based on the process id

    #If DSM from excel or csv then do that otherwise fetch from back end
    #DSM and processes should be gettable at the same time. 
    dsm = None

    #BUG entering pid as param to the Simulation. Will fail on the separate dsm method since that one wants an actual process. (or a name)
    sim = Simulation(flow_time, flow_rate, flow_process, simulation_runtime, discount_rate, populate_processes(vcs_rows, market_input), populate_non_tech_processes(vcs_rows, market_input), dsm)
    sim.run_simulation()

    return models.Simulation(
        time=sim.time_steps,
        cumulative_NPV=sim.cum_NPV,
        processes=sim.processes
    )

def fetch_sim_data(db_connection: PooledMySQLConnection, vcs_id: int):

    query = f'SELECT cvs_vcs_rows.id, `index`, cvs_vcs_rows.iso_process, cvs_iso_processes.name as iso_name, \
            subprocess, cvs_subprocesses.name as sub_name, from, to, time, cost, revenue FROM cvs_vcs_rows \
            LEFT OUTER JOIN cvs_iso_processes ON cvs_vcs_rows.iso_process = cvs_iso_processes.id \
            LEFT OUTER JOIN cvs_subprocesses ON cvs_vcs_rows.subprocess = cvs_subprocesses.id \
            LEFT OUTER JOIN cvs_process_nodes ON cvs_vcs_rows.id = cvs_process_nodes.vcs_row \
            LEFT OUTER JOIN cvs_nodes ON cvs_process_nodes.id = cvs_nodes.id \
            LEFT OUTER JOIN cvs_market_input ON cvs_vcs_rows.id = cvs_market_input.vcs_row \
            WHERE cvs_vcs_rows.vcs = %s ORDER BY `index`'
    with db_connection.cursor(prepared=True) as cursor:
        cursor.execute(query, [vcs_id])
        res = cursor.fetchall()

        res = [dict(zip(cursor.column_names, row)) for row in res]


    return populate_data(res)

def populate_data(db_result) -> Tuple[List[Process], List[Process], dict]:
    
    dsm = dict()
    processes = []
    non_tech_processes = []

    nodes = dict()
    start_node = None
    #Need to know how many processes there will be. Is there a way to filter out that from the nodes?
    #ATM it's just the length of all the nodes. 

    
    for res in db_result:
        if res['iso_name'] is not None and res['sub_name'] is None:
            p = Process(res['time'], res['cost'], res['revenue'], res['iso_name'], TimeFormat.YEAR)
        elif res['iso_name'] is None and res['sub_name'] is not None:
            p = Process(res['time'], res['cost'], res['revenue'], res['sub_name'], TimeFormat.YEAR)
        else:
            raise ProcessNotFoundException
        processes.append(p)

    """
    process_amount = len(bpmn.nodes)

    for process_node in bpmn.nodes: #Problem with the indexes - how do we know which process goes where?
        nodes.update({process_node.id: process_node})
        if process_node.from_node is None:
            start_node = process_node.id

    while len(nodes.keys()) > 0: #Skulle kunna enumerate kke. El köra från i till len(nodes) <- det funkar om evauleringen av condition inte sker under runtime. 
        node = nodes.pop(start_node)
        if node.vcs_row.iso_process is not None and node.vcs_row.subprocess is None:
         #   processes.append(Process(time,cost,revenue, node.vcs_row.iso_process.name, time_format))
            dsm.update({node.vcs_row.iso_process.name: []}) #Fuck här hamnar vi i indexproblem igen...
        elif node.vcs_row.iso_process is None and node.vcs_row.subprocess is not None:
          #  processes.append(Process(time,cost,revenue, node.vcs_row.subprocess.name, time_format))
          continue
        else:
            raise ProcessNotFoundException
    """
    return processes, non_tech_processes, dsm

def populate_processes(vcs_rows: List[VcsRow], market_input: List[MarketInputGet]) -> List[models.Process]:
    processes = []

    for row in vcs_rows:
        if (row.iso_process and row.iso_process.category == 'Technical processes') \
                or (row.subprocess and row.subprocess.parent_process.category == 'Technical processes'):
            if row.iso_process:
                name = row.iso_process.name
            else:
                name = row.subprocess.name

            for mi in market_input:
                if mi.vcs_row == row.id:
                    process = Process(mi.time, mi.cost, mi.revenue, name)
                    processes.append(process)
    return processes

def populate_non_tech_processes(vcs_rows: List[VcsRow], market_input: List[MarketInputGet]) -> List[models.NonTechnicalProcess]:
    non_tech_processes = []
    for row in vcs_rows:
        if (row.iso_process and row.iso_process.category != 'Technical processes') \
            or (row.subprocess and row.subprocess.parent_process.category != 'Techical processes'):
                if row.iso_process:
                    name = row.iso_process.name
                else: 
                    name = row.subprocess.name
            
                for mi in market_input:
                    if mi.vcs_row == row.id:
                        non_tech_process = models.NonTechnicalProcess(
                            name=name,
                            cost=market_input.cost,
                            revenue=market_input.revenue
                        )
                        non_tech_processes.append(non_tech_process)
    return non_tech_processes

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
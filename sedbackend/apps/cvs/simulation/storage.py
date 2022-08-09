
import tempfile
from fastapi import UploadFile
from mysql.connector.pooling import PooledMySQLConnection
import pandas as pd
import multiprocessing as mp

from fastapi.logger import logger

import desim.interface as des
from desim.data import NonTechCost, TimeFormat
from desim.simulation import Process

from typing import List
from sedbackend.apps.cvs import vcs
from sedbackend.apps.cvs.design.models import QuantifiedObjective
from sedbackend.libs.mysqlutils.builder import FetchType, MySQLStatementBuilder

from sedbackend.libs.parsing.parser import NumericStringParser
from sedbackend.libs.parsing import expressions as expr
from sedbackend.apps.cvs.simulation import models
from sedbackend.apps.cvs.market_input.models import MarketInputGet
import sedbackend.apps.cvs.simulation.exceptions as e
import sedbackend.apps.cvs.vcs.implementation as vcs_impl
import sedbackend.apps.cvs.market_input.implementation as mi_impl
import sedbackend.apps.cvs.life_cycle.implementation as lifecycle_impl
from sedbackend.apps.cvs.vcs.models import VcsRow
from sedbackend.apps.cvs.design import implementation as design_impl

TIME_FORMAT_DICT = dict({
    'year': TimeFormat.YEAR, 
    'month': TimeFormat.MONTH, 
    'week': TimeFormat.WEEK, 
    'day': TimeFormat.DAY, 
    'hour': TimeFormat.HOUR})

def run_sim_with_csv_dsm(db_connection: PooledMySQLConnection, vcs_id: int, flow_time: float,
                flow_rate: float, process_id: int, simulation_runtime: float, discount_rate: float, 
                non_tech_add: models.NonTechCost, dsm_csv: UploadFile, user_id: int) -> models.Simulation:

    if dsm_csv is None:
        raise e.DSMFileNotFoundException
    
    try:
        tmp_csv = tempfile.TemporaryFile()  #Workaround because current python version doesn't support 
        tmp_csv.write(dsm_csv.file.read())      #readable() attribute on SpooledTemporaryFile which UploadFile 
        tmp_csv.seek(0)                     #is an alias for. PR is accepted for python v3.12, see https://github.com/python/cpython/pull/29560

        dsm = get_dsm_from_csv(tmp_csv) #This should hopefully open up the file for the processor. 
        if dsm is None:
            raise e.DSMFileNotFoundException
    except Exception as exc:
        logger.debug(exc)
    finally:
        tmp_csv.close()

    res = get_sim_data(db_connection, vcs_id)

    processes, non_tech_processes = populate_processes(non_tech_add, res, db_connection, vcs_id)
    """
    #print(dsm.keys())
    for key in dsm.keys():
        p = None
        for r in res:
            if r['iso_name'] is not None and r['sub_name'] is None:
                if key == r['iso_name']:
                    p = Process(r['time'], r['cost'], r['revenue'], r['iso_name'], non_tech_add, TIME_FORMAT_DICT.get(r['time_unit'].lower()))
                    processes.append(p)
                    if r['id'] == process_id:
                        flow_process = p
                    break
            elif r['iso_name'] is None and r['sub_name'] is not None:
                if key == r['sub_name']:
                    p = Process(r['time'], r['cost'], r['revenue'], r['sub_name'], non_tech_add, TIME_FORMAT_DICT.get(r['time_unit'].lower()))
                    processes.append(p)
                    if r['id'] == process_id:
                        flow_process = p
                    break
            else:
                raise e.ProcessNotFoundException
        
    
    for r in res:
        if r['iso_name'] is not None:
            if r['iso_name'] not in dsm.keys() and r['category'] != 'Technical process':
                p = models.NonTechnicalProcess(name=r['iso_name'], cost=r['cost'], revenue=r['revenue'])
                non_tech_processes.append(p)
        elif r['sub_name'] is not None:
            if r['sub_name'] not in dsm.keys():
                p = models.NonTechnicalProcess(name=r['sub_name'], cost=r['cost'], revenue=r['revenue'])
                non_tech_processes.append(p)
    
        #print([p.name for p in processes])

    #print(flow_process.name)        
    
   """

    sim = des.Des()
    time, cum_npv, _, _ = sim.run_simulation(flow_time, flow_rate, process_id, processes, non_tech_processes, non_tech_add, dsm, discount_rate, simulation_runtime)
    #sim = Simulation(flow_time, flow_rate, flow_process, simulation_runtime, discount_rate, processes, non_tech_processes, non_tech_add, dsm)
    #sim.run_simulation()

    return models.Simulation(
        time=time,
        cumulative_NPV = cum_npv,
        processes=[models.Process(name=p.name, time=p.time, cost=p.cost, revenue=p.revenue) for p in processes]
    )

def run_sim_with_xlsx_dsm(db_connection: PooledMySQLConnection, vcs_id: int, flow_time: float,
                flow_rate: float, process_id: int, simulation_runtime: float, discount_rate: float, 
                non_tech_add: models.NonTechCost, dsm_xlsx: UploadFile, user_id: int) -> models.Simulation:

    try:
        tmp_xlsx = tempfile.TemporaryFile()  #Workaround because current python version doesn't support 
        tmp_xlsx.write(dsm_xlsx.file.read()) #readable() attribute on SpooledTemporaryFile which UploadFile 
        tmp_xlsx.seek(0)                     #is an alias for. PR is accepted for python v3.12, see https://github.com/python/cpython/pull/29560
        if dsm_xlsx is None:
            raise e.DSMFileNotFoundException

        dsm = get_dsm_from_excel(tmp_xlsx)
        if dsm is None:
            raise e.DSMFileNotFoundException
    finally:
        tmp_xlsx.close()

    res = get_sim_data(db_connection, vcs_id)
    #processes = []
    
    """
    for key in dsm.keys():
        for r in res:
            if r['iso_name'] is not None and r['sub_name'] is None:
                if key == r['iso_name']:
                    p = Process(r['time'], r['cost'], r['revenue'], r['iso_name'], non_tech_add, TIME_FORMAT_DICT.get(r['time_unit'].lower()))
                    processes.append(p)
                    if r['id'] == process_id:
                        flow_process = p
                    break
            elif r['iso_name'] is None and r['sub_name'] is not None:
                if key == r['sub_name']:
                    p = Process(r['time'], r['cost'], r['revenue'], r['sub_name'], non_tech_add, TIME_FORMAT_DICT.get(r['time_unit'].lower()))
                    processes.append(p)
                    if r['id'] == process_id:
                        flow_process = p
                    break
            else:
                raise e.ProcessNotFoundException
            

    non_tech_processes = []   
    for r in res:
        if r['iso_name'] is not None:
            if r['iso_name'] not in dsm.keys() and r['category'] != 'Technical process':
                p = models.NonTechnicalProcess(name=r['iso_name'], cost=r['cost'], revenue=r['revenue'])
                non_tech_processes.append(p)
        elif r['sub_name'] is not None:
            if r['sub_name'] not in dsm.keys():
                p = models.NonTechnicalProcess(name=r['sub_name'], cost=r['cost'], revenue=r['revenue'])
                non_tech_processes.append(p)
    """

    processes, non_tech_processes = populate_processes(non_tech_add, res, db_connection, vcs_id)
    sim = des.Des()
    #sim = Simulation(flow_time, flow_rate, flow_process, simulation_runtime, discount_rate, processes, non_tech_processes, non_tech_add, dsm)
    time, cum_npv, _, _ = sim.run_simulation(flow_time, flow_rate, process_id, processes, non_tech_processes, non_tech_add, dsm, discount_rate, simulation_runtime)

    return models.Simulation(
        time=time,
        cumulative_NPV = cum_npv,
        processes=[models.Process(name=p.name, time=p.time, cost=p.cost, revenue=p.revenue) for p in processes]
    )

def run_simulation(db_connection: PooledMySQLConnection, vcs_id: int, flow_time: float, 
        flow_rate: float, process_id: int, simulation_runtime: float, discount_rate: float,
        non_tech_add: models.NonTechCost, user_id: int) -> models.Simulation:
    
    res = get_sim_data(db_connection, vcs_id)

    """
    processes = []
    non_tech_processes = []
    for row in res:
        if row['iso_name'] is not None and row['sub_name'] is None:
            if row['category'] != 'Technical processes':
                non_tech = models.NonTechnicalProcess(cost=row['cost'], revenue=row['revenue'], name=row['iso_name'])
                non_tech_processes.append(non_tech)
            else:
                p = Process(row['time'], row['cost'], row['revenue'], row['iso_name'],non_tech_add, TIME_FORMAT_DICT.get(row['time_unit'].lower()))
                processes.append(p)
                if row['id'] == process_id:
                    flow_process = p     
        elif row['iso_name'] is None and row['sub_name'] is not None:
            p = Process(row['time'], row['cost'], row['revenue'], row['sub_name'], non_tech_add, TIME_FORMAT_DICT.get(row['time_unit'].lower()))
            processes.append(p)
            if row['id'] == process_id:
                flow_process = p
        else:
            raise e.ProcessNotFoundException
    """
    processes, non_tech_processes = populate_processes(non_tech_add, res, db_connection, vcs_id)
    
    dsm = create_simple_dsm(processes) #TODO Change to using BPMN

    sim = des.Des()
    time, cum_npv, _, _ = sim.run_simulation(flow_time, flow_rate, process_id, processes, non_tech_processes, non_tech_add, dsm, discount_rate, simulation_runtime)
    
    return models.Simulation(
        time=time,
        cumulative_NPV=cum_npv,
        processes=[models.Process(name=p.name, time=p.time, cost=p.cost, revenue=p.revenue) for p in processes]
    )


def run_sim_mp(db_connection: PooledMySQLConnection, vcs_id: int, flow_time: float, 
        flow_rate: float, process_id: int, simulation_runtime: float, discount_rate: float,
        non_tech_add: models.NonTechCost, user_id: int) -> models.Simulation:

    res = get_sim_data(db_connection, vcs_id)
    processes, non_tech_processes = populate_processes(non_tech_add, res, db_connection, vcs_id)


    dsm = create_simple_dsm(processes) #TODO Change to using BPMN

    sim = des.Des()
    time, cum_npv, cost, revenue = sim.run_parallell_simulations(flow_time, flow_rate, process_id, processes, non_tech_processes, non_tech_add, dsm, discount_rate, simulation_runtime)

    """
    processes = []
    non_tech_processes = []
    for row in res:
        if row['iso_name'] is not None and row['sub_name'] is None:
            if row['category'] != 'Technical processes':
                non_tech = models.NonTechnicalProcess(cost=row['cost'], revenue=row['revenue'], name=row['iso_name'])
                non_tech_processes.append(non_tech)
            else:
                p = Process(row['time'], row['cost'], row['revenue'], row['iso_name'], non_tech_add, TIME_FORMAT_DICT.get(row['time_unit'].lower()))
                processes.append(p)
                if row['id'] == process_id:
                    flow_process = p     
        elif row['iso_name'] is None and row['sub_name'] is not None:
            p = Process(row['time'], row['cost'], row['revenue'], row['sub_name'], non_tech_add, TIME_FORMAT_DICT.get(row['time_unit'].lower()))
            processes.append(p)
            if row['id'] == process_id:
                flow_process = p
        else:
            raise e.ProcessNotFoundException
    """

    return models.Simulation(
        time=time,
        cumulative_NPV=cum_npv,
        processes=[models.Process(name=p.name, time=p.time, cost=p.cost, revenue=p.revenue) for p in processes]
    )

def populate_processes(non_tech_add: NonTechCost, db_results, db_connection: PooledMySQLConnection, vcs: int, technical_processes: List = [], non_tech_processes: List = []):
    nsp = NumericStringParser()

    for row in db_results:
        qo_values = get_quantified_values(db_connection, row['id'], 2)
        mi_values = get_market_values(db_connection, row['id'], vcs)
        if row['iso_name'] is not None and row['sub_name'] is None:
            if row['category'] != 'Technical processes':
                try:
                    non_tech = models.NonTechnicalProcess(cost=nsp.eval(parse_formula(row['cost'], qo_values, mi_values)), 
                        revenue=nsp.eval(parse_formula(row['revenue'], qo_values, mi_values)), name=row['iso_name'])
                except Exception as exc:
                    logger.debug(f'{exc.__class__}, {exc}')
                    raise e.FormulaEvalException(row['id'])
                non_tech_processes.append(non_tech)
            else:
                try:
                    p = Process(row['id'], 
                        nsp.eval(parse_formula(row['time'], qo_values, mi_values)), 
                        nsp.eval(parse_formula(row['cost'], qo_values, mi_values)), 
                        nsp.eval(parse_formula(row['revenue'], qo_values, mi_values)), 
                        row['iso_name'], non_tech_add, TIME_FORMAT_DICT.get(row['time_unit'].lower())
                        )
                    if p.time < 0:
                        print(f'Problem at process: {p.id}')
                except Exception as exc:
                    logger.debug(f'{exc.__class__}, {exc}')
                    raise e.FormulaEvalException(row['id'])
                technical_processes.append(p)    
        elif row['iso_name'] is None and row['sub_name'] is not None:
            try:
                p = Process(row['id'], 
                    nsp.eval(parse_formula(row['time'], qo_values, mi_values)), 
                    nsp.eval(parse_formula(row['cost'], qo_values, mi_values)), 
                    nsp.eval(parse_formula(row['revenue'], qo_values, mi_values)), 
                    row['sub_name'], non_tech_add, TIME_FORMAT_DICT.get(row['time_unit'].lower())
                    )
                
                if p.time < 0:
                    print(f'Problem at process: {p.id}')
            except Exception as exc:
                logger.debug(f'{exc.__class__}, {exc}')
                raise e.FormulaEvalException(row['id'])
            technical_processes.append(p)
        else:
            raise e.ProcessNotFoundException
    
    return technical_processes, non_tech_processes

def get_sim_data(db_connection: PooledMySQLConnection, vcs_id: int):
    query = f'SELECT cvs_vcs_rows.id, cvs_vcs_rows.iso_process, cvs_iso_processes.name as iso_name, category, \
            subprocess, cvs_subprocesses.name as sub_name, time, time_unit, cost, revenue FROM cvs_vcs_rows \
            LEFT OUTER JOIN cvs_iso_processes ON cvs_vcs_rows.iso_process = cvs_iso_processes.id \
            LEFT OUTER JOIN cvs_subprocesses ON cvs_vcs_rows.subprocess = cvs_subprocesses.id \
            LEFT OUTER JOIN cvs_design_mi_formulas ON cvs_vcs_rows.id = cvs_design_mi_formulas.vcs_row \
            WHERE cvs_vcs_rows.vcs = %s ORDER BY `index`'
    with db_connection.cursor(prepared=True) as cursor:
        cursor.execute(query, [vcs_id])
        res = cursor.fetchall()
        res = [dict(zip(cursor.column_names, row)) for row in res]
    return res

def get_quantified_values(db_connection: PooledMySQLConnection, vcs_row_id: int, design: int):

    select_statement = MySQLStatementBuilder(db_connection)
    res = select_statement \
        .select('cvs_quantified_objective_values', ['name', 'value'])\
        .inner_join('cvs_quantified_objectives', 'cvs_quantified_objective_values.value_driver = cvs_quantified_objectives.value_driver') \
        .inner_join('cvs_formulas_quantified_objectives', 'cvs_formulas_quantified_objectives.value_driver = cvs_quantified_objective_values.value_driver')\
        .where('formulas = %s and design = %s', [vcs_row_id, design])\
        .execute(fetch_type=FetchType.FETCH_ALL, dictionary=True)
    
    return res

def get_market_values(db_connection: PooledMySQLConnection, vcs_row_id: int, vcs: int):

    select_statement = MySQLStatementBuilder(db_connection)
    res = select_statement \
        .select('cvs_market_values', ['name', 'value'])\
        .inner_join('cvs_market_inputs', 'cvs_market_values.market_input = cvs_market_inputs.id')\
        .inner_join('cvs_formulas_market_inputs', 'cvs_formulas_market_inputs.market_input = cvs_market_values.market_input')\
        .where('formulas = %s and vcs = %s', [vcs_row_id, vcs])\
        .execute(fetch_type=FetchType.FETCH_ALL, dictionary=True)
    
    return res

def parse_formula(formula: str, qo_values, mi_values):
    new_formula = formula
    for qo in qo_values: 
        new_formula = expr.replace_all(qo['name'], qo['value'], new_formula)
    
    for mi in mi_values:
        new_formula = expr.replace_all(mi['name'], mi['value'], new_formula)
    
    return new_formula

def check_entity_rate(db_results):
    rate_check = True
    for i in range(len(db_results)- 1):
        if db_results[i]['rate'] == 'per_product' and db_results[i+1]['rate'] == 'per_project': #TODO check for technical/non-technical processes
            rate_check = False
            break
    
    return rate_check

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


"""
Query for fetching categories for both subprocesses and normal processes. 

SELECT cvs_vcs_rows.id, `index`, cvs_vcs_rows.iso_process, cvs_iso_processes.name as iso_name, category,
            subprocess, sub_name,  sub_cat,  `from`, `to`, time, cost, revenue FROM cvs_vcs_rows 
            LEFT OUTER JOIN cvs_iso_processes ON cvs_vcs_rows.iso_process = cvs_iso_processes.id 
			LEFT OUTER JOIN (SELECT cvs_subprocesses.id as sub_id, category as sub_cat, cvs_subprocesses.name as sub_name FROM cvs_subprocesses INNER JOIN cvs_iso_processes ON cvs_iso_processes.id = cvs_subprocesses.iso_process) as sub1
            ON sub1.sub_id = cvs_vcs_rows.subprocess
            #cvs_subprocesses ON cvs_vcs_rows.subprocess = cvs_subprocesses.id
            LEFT OUTER JOIN cvs_process_nodes ON cvs_vcs_rows.id = cvs_process_nodes.vcs_row 
            LEFT OUTER JOIN cvs_nodes ON cvs_process_nodes.id = cvs_nodes.id 
            LEFT OUTER JOIN cvs_market_input ON cvs_vcs_rows.id = cvs_market_input.vcs_row 
            WHERE cvs_vcs_rows.vcs = 5 ORDER BY `index`;


"""
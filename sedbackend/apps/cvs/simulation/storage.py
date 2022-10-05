
import tempfile
from fastapi import UploadFile
from mysql.connector.pooling import PooledMySQLConnection
import pandas as pd
import multiprocessing as mp

from fastapi.logger import logger

import desim.interface as des
from desim.data import NonTechCost, TimeFormat, SimResults
from desim.simulation import Process

from typing import List, Optional

from sedbackend.libs.mysqlutils.builder import FetchType, MySQLStatementBuilder

from sedbackend.libs.parsing.parser import NumericStringParser
from sedbackend.libs.parsing import expressions as expr
from sedbackend.apps.cvs.simulation import models
import sedbackend.apps.cvs.simulation.exceptions as e
import sedbackend.apps.cvs.market_input.implementation as mi_impl
import sedbackend.apps.cvs.life_cycle.implementation as lifecycle_impl
from sedbackend.apps.cvs.vcs.models import VcsRow
from sedbackend.apps.cvs.design import implementation as design_impl

TIME_FORMAT_DICT = dict({
    'year': TimeFormat.YEAR, 
    'month': TimeFormat.MONTH, 
    'week': TimeFormat.WEEK, 
    'day': TimeFormat.DAY, 
    'hour': TimeFormat.HOUR,
    #'minutes': TimeFormat.MINUTES
})

def run_sim_with_csv_dsm(db_connection: PooledMySQLConnection, vcs_id: int, flow_time: float,
                flow_rate: float, process_id: int, simulation_runtime: float, discount_rate: float, 
                non_tech_add: models.NonTechCost, dsm_csv: UploadFile, design_ids: List[int], 
                normalized_npv: bool, user_id: int) -> List[models.Simulation]:

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

    if not check_entity_rate(res, process_id):
        raise e.RateWrongOrderException
    

    if design_ids is None or []:
        raise e.DesignIdsNotFoundException

    design_results = []
    for design_id in design_ids:
        processes, non_tech_processes = populate_processes(non_tech_add, res, db_connection, vcs_id, design_id)

        sim = des.Des()
        time, cum_npv, _, _ = sim.run_simulation(flow_time, flow_rate, process_id, processes, non_tech_processes, non_tech_add, dsm, discount_rate, simulation_runtime)
    #sim = Simulation(flow_time, flow_rate, flow_process, simulation_runtime, discount_rate, processes, non_tech_processes, non_tech_add, dsm)
    #sim.run_simulation()

        design_res = models.Simulation(
            time=time,
            cumulative_NPV = cum_npv,
            processes=[models.Process(name=p.name, time=p.time, cost=p.cost, revenue=p.revenue) for p in processes]
            )
        design_results.append(design_res)
    
    return design_results

def run_sim_with_xlsx_dsm(db_connection: PooledMySQLConnection, vcs_id: int, flow_time: float,
                flow_rate: float, process_id: int, simulation_runtime: float, discount_rate: float, 
                non_tech_add: models.NonTechCost, dsm_xlsx: UploadFile, design_ids: List[int], 
                normalized_npv: bool, user_id: int) -> List[models.Simulation]:

    if dsm_xlsx is None:
            raise e.DSMFileNotFoundException

    try:
        tmp_xlsx = tempfile.TemporaryFile()  #Workaround because current python version doesn't support 
        tmp_xlsx.write(dsm_xlsx.file.read()) #readable() attribute on SpooledTemporaryFile which UploadFile 
        tmp_xlsx.seek(0)                     #is an alias for. PR is accepted for python v3.12, see https://github.com/python/cpython/pull/29560
        
        dsm = get_dsm_from_excel(tmp_xlsx)
        if dsm is None:
            raise e.DSMFileNotFoundException
    except Exception as exc:
        logger.debug(exc)
    finally:
        tmp_xlsx.close()

    res = get_sim_data(db_connection, vcs_id)
    #processes = []
    
    if not check_entity_rate(res, process_id):
        raise e.RateWrongOrderException


    if design_ids is None or []:
        #for design in design_impl.get_all_designs(1):
        #    design_ids.append(design.id)
        raise e.DesignIdsNotFoundException

    design_results = []
    for design_id in design_ids:
        processes, non_tech_processes = populate_processes(non_tech_add, res, db_connection, vcs_id, design_id)
        sim = des.Des()
    
        try:
            time, cum_npv, _, _ = sim.run_simulation(flow_time, flow_rate, process_id, processes, non_tech_processes, non_tech_add, dsm, discount_rate, simulation_runtime)
        except Exception as exc:
            logger.debug(f'{exc.__class__}, {exc}')
            raise e.SimulationFailedException

        design_res = models.Simulation(
            time=time,
            cumulative_NPV = cum_npv,
            processes=[models.Process(name=p.name, time=p.time, cost=p.cost, revenue=p.revenue) for p in processes]
        )

        design_results.append(design_res)
    
    return design_results

def run_simulation(db_connection: PooledMySQLConnection, vcs_id: int, flow_time: float, 
        flow_rate: float, process_id: int, simulation_runtime: float, discount_rate: float,
        non_tech_add: models.NonTechCost, design_ids: List[int], normalized_npv: bool,  user_id: int) -> List[models.Simulation]:
    
    res = get_sim_data(db_connection, vcs_id)

    if not check_entity_rate(res, process_id):
        raise e.RateWrongOrderException
    
    if design_ids is None or []:
        #for design in design_impl.get_all_designs(1):
        #    design_ids.append(design.id)
        raise e.DesignIdsNotFoundException

    design_results = []
    for design_id in design_ids:
        processes, non_tech_processes = populate_processes(non_tech_add, res, db_connection, vcs_id, design_id)
    
        dsm = create_simple_dsm(processes) #TODO Change to using BPMN

        sim = des.Des()

        try:
            time, cum_npv, _, _ = sim.run_simulation(flow_time, flow_rate, process_id, processes, non_tech_processes, non_tech_add, dsm, discount_rate, simulation_runtime)
    
        except Exception as exc:
            logger.debug(f'{exc.__class__}, {exc}')
            raise e.SimulationFailedException

        design_res = models.Simulation(
            time=time,
            cumulative_NPV=cum_npv,
            processes=[models.Process(name=p.name, time=p.time, cost=p.cost, revenue=p.revenue) for p in processes]
        )
        design_results.append(design_res)
    
    return design_results


def run_sim_monte_carlo(db_connection: PooledMySQLConnection, vcs_id: int, flow_time: float, 
        flow_rate: float, process_id: int, simulation_runtime: float, discount_rate: float,
        non_tech_add: models.NonTechCost, design_ids: List[int], 
        runs: int, normalized_npv: bool, 
        user_id: int = None) -> List[models.SimulationMonteCarlo]:

    res = get_sim_data(db_connection, vcs_id)
    #print(res)
    if not check_entity_rate(res, process_id):
        raise e.RateWrongOrderException
    
   

    if design_ids is None or []:
        #for design in design_impl.get_all_designs(1):
        #    design_ids.append(design.id)
        raise e.DesignIdsNotFoundException

    design_results = []
    for design_id in design_ids:
        processes, non_tech_processes = populate_processes(non_tech_add, res, db_connection, vcs_id, design_id)
        logger.debug('Fetched Processes and non-techproc')
        dsm = create_simple_dsm(processes) #TODO Change to using BPMN AND move out of the for loop
        

        sim = des.Des()

        try:
            results = sim.run_parallell_simulations(flow_time, flow_rate, process_id, processes, non_tech_processes, non_tech_add, dsm, discount_rate, simulation_runtime, runs)
    
        except Exception as exc:
            logger.debug(f'{exc.__class__}, {exc}')
            raise e.SimulationFailedException

        if normalized_npv:
            m_npv = results.normalize_npv()
        else:
            m_npv = results.mean_npv()

        sim_res = models.SimulationMonteCarlo(
            time=results.timesteps[-1],
            mean_NPV=m_npv,
            max_NPVs=results.all_max_npv(),
            mean_payback_time=results.mean_npv_payback_time()
            )
        design_results.append(sim_res)
    
    return design_results

def populate_processes(non_tech_add: NonTechCost, db_results, db_connection: PooledMySQLConnection, vcs: int, design: int, technical_processes: List = [], non_tech_processes: List = []):
    nsp = NumericStringParser()

    for row in db_results:
        vd_values = get_vd_design_values(db_connection, row['id'], design)
        mi_values = get_market_values(db_connection, row['id'], vcs)
        if row['category'] != 'Technical processes':
            try:
                non_tech = models.NonTechnicalProcess(cost=nsp.eval(parse_formula(row['cost'], vd_values, mi_values)), 
                    revenue=nsp.eval(parse_formula(row['revenue'], vd_values, mi_values)), name=row['iso_name'])
            except Exception as exc:
                logger.debug(f'{exc.__class__}, {exc}')
                raise e.FormulaEvalException(row['id'])
            non_tech_processes.append(non_tech)
            
        elif row['iso_name'] is not None and row['sub_name'] is None:
            try:
                time = nsp.eval(parse_formula(row['time'], vd_values, mi_values))
                cost_formula = parse_formula(row['cost'], vd_values, mi_values)
                revenue_formula = parse_formula(row['revenue'], vd_values, mi_values)
                p = Process(row['id'], 
                    time, 
                    nsp.eval(expr.replace_all('time', time, cost_formula)), 
                    nsp.eval(expr.replace_all('time', time, revenue_formula)), 
                    row['iso_name'], non_tech_add, TIME_FORMAT_DICT.get(row['time_unit'].lower())
                    )
                if p.time < 0:
                    raise e.NegativeTimeException(row['id'])
            except Exception as exc:
                logger.debug(f'{exc.__class__}, {exc}')
                raise e.FormulaEvalException(row['id'])
            technical_processes.append(p)    
        elif row['sub_name'] is not None:
            try:
                time = nsp.eval(parse_formula(row['time'], vd_values, mi_values))
                cost_formula = parse_formula(row['cost'], vd_values, mi_values)
                revenue_formula = parse_formula(row['revenue'], vd_values, mi_values)
                p = Process(row['id'], 
                    time, 
                    nsp.eval(expr.replace_all('time', time, cost_formula)), 
                    nsp.eval(expr.replace_all('time', time, revenue_formula)), 
                    row['sub_name'], non_tech_add, TIME_FORMAT_DICT.get(row['time_unit'].lower())
                    )
                
                if p.time < 0:
                    raise e.NegativeTimeException(row['id'])
            except Exception as exc:
                logger.debug(f'{exc.__class__}, {exc}')
                raise e.FormulaEvalException(row['id'])
            technical_processes.append(p)
        else:
            raise e.ProcessNotFoundException
    
    return technical_processes, non_tech_processes

def get_sim_data(db_connection: PooledMySQLConnection, vcs_id: int):
    query = f'SELECT cvs_vcs_rows.id, cvs_vcs_rows.iso_process, cvs_iso_processes.name as iso_name, category, \
            subprocess, cvs_subprocesses.name as sub_name, time, time_unit, cost, revenue, rate FROM cvs_vcs_rows \
            LEFT OUTER JOIN cvs_subprocesses ON cvs_vcs_rows.subprocess = cvs_subprocesses.id \
            LEFT OUTER JOIN cvs_iso_processes ON cvs_vcs_rows.iso_process = cvs_iso_processes.id \
                OR cvs_subprocesses.iso_process = cvs_iso_processes.id \
            LEFT OUTER JOIN cvs_design_mi_formulas ON cvs_vcs_rows.id = cvs_design_mi_formulas.vcs_row \
            WHERE cvs_vcs_rows.vcs = %s ORDER BY `index`'
    with db_connection.cursor(prepared=True) as cursor:
        cursor.execute(query, [vcs_id])
        res = cursor.fetchall()
        res = [dict(zip(cursor.column_names, row)) for row in res]
    return res

def get_vd_design_values(db_connection: PooledMySQLConnection, vcs_row_id: int, design: int): #TODO fetch value driver values. 

    select_statement = MySQLStatementBuilder(db_connection)
    res = select_statement \
        .select('cvs_vd_design_values', ['id', 'design', 'name',  'value'])\
        .inner_join('cvs_value_drivers', 'cvs_vd_design_values.value_driver = id') \
        .inner_join('cvs_formulas_value_drivers', 'cvs_formulas_value_drivers.value_driver = cvs_vd_design_values.value_driver')\
        .where('formulas = %s and design = %s', [vcs_row_id, design])\
        .execute(fetch_type=FetchType.FETCH_ALL, dictionary=True)
    
    return res

def get_market_values(db_connection: PooledMySQLConnection, vcs_row_id: int, vcs: int):

    select_statement = MySQLStatementBuilder(db_connection)
    res = select_statement \
        .select('cvs_market_values', ['id', 'name', 'value'])\
        .inner_join('cvs_market_inputs', 'cvs_market_values.market_input = cvs_market_inputs.id')\
        .inner_join('cvs_formulas_market_inputs', 'cvs_formulas_market_inputs.market_input = cvs_market_values.market_input')\
        .where('formulas = %s and vcs = %s', [vcs_row_id, vcs])\
        .execute(fetch_type=FetchType.FETCH_ALL, dictionary=True)
    
    return res

def parse_formula(formula: str, vd_values, mi_values): #TODO fix how the formulas are parsed
    new_formula = formula
    vd_ids = expr.get_prefix_ids('vd', new_formula)
    mi_ids = expr.get_prefix_ids('mi', new_formula)
    for vd in vd_values:
        for id in vd_ids:
            if int(id) == vd['id']:
                new_formula = expr.replace_all('vd'+id, vd['value'], new_formula)
    for mi in mi_values:
        for id in mi_ids:
            if int(id) == mi['id']:
                new_formula = expr.replace_all('mi'+id, mi['value'], new_formula)
    
    return new_formula

def check_entity_rate(db_results, flow_process_id: int):
    rate_check = True
    flow_process_index = len(db_results)

    for i in range(len(db_results)- 1):
        if db_results[i]['id'] == flow_process_id: 
            flow_process_index = i
        if db_results[i]['rate'] == 'per_product' and db_results[i+1]['rate'] == 'per_project' and i >= flow_process_index: #TODO check for technical/non-technical processes
            
            if db_results[i]['category'] == 'Technical processes' and db_results[i+1]['category'] == 'Technical processes':
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

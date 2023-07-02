import sys
import tempfile
from fastapi import UploadFile
from mysql.connector.pooling import PooledMySQLConnection
import pandas as pd
from mysql.connector import Error

from fastapi.logger import logger

from desim import interface as des
from desim.data import NonTechCost, TimeFormat
from desim.simulation import Process
import os

from typing import List
from sedbackend.apps.cvs.design.models import ValueDriverDesignValue
from sedbackend.apps.cvs.design.storage import get_all_designs

from mysqlsb import FetchType, MySQLStatementBuilder

from sedbackend.libs.formula_parser.parser import NumericStringParser
from sedbackend.libs.formula_parser import expressions as expr
from sedbackend.apps.cvs.simulation import models
import sedbackend.apps.cvs.simulation.exceptions as e
from sedbackend.apps.cvs.vcs import storage as vcs_storage
from sedbackend.apps.cvs.life_cycle import storage as life_cycle_storage
from sedbackend.apps.core.files import storage as file_storage

SIM_SETTINGS_TABLE = "cvs_simulation_settings"
SIM_SETTINGS_COLUMNS = ['project', 'time_unit', 'flow_process', 'flow_start_time', 'flow_time',
                        'interarrival_time', 'start_time', 'end_time', 'discount_rate', 'non_tech_add', 'monte_carlo',
                        'runs']

TIME_FORMAT_DICT = dict({
    'year': TimeFormat.YEAR,
    'month': TimeFormat.MONTH,
    'week': TimeFormat.WEEK,
    'day': TimeFormat.DAY,
    'hour': TimeFormat.HOUR,
    'minutes': TimeFormat.MINUTES
})


# TODO: Run simulation on DSM file
def get_dsm_from_file(db_connection: PooledMySQLConnection, user_id: int, project_id: int,
                          sim_params: models.FileParams,
                          dsm_file: UploadFile) -> dict:
    _, file_extension = os.path.splitext(dsm_file.filename)

    dsm = {}

    if file_extension == '.xlsx':
        try:
            tmp_xlsx = tempfile.TemporaryFile()  # Workaround because current python version doesn't support
            tmp_xlsx.write(dsm_file.file.read())  # readable() attribute on SpooledTemporaryFile which UploadFile
            tmp_xlsx.seek(
                0)  # is an alias for. PR is accepted for python v3.12, see https://github.com/python/cpython/pull/29560

            dsm = get_dsm_from_excel(tmp_xlsx)
            if dsm is None:
                raise e.DSMFileNotFoundException
        except Exception as exc:
            logger.debug(exc)
        finally:
            tmp_xlsx.close()
    elif file_extension == '.csv':
        try:
            tmp_csv = tempfile.TemporaryFile()  # Workaround because current python version doesn't support
            tmp_csv.write(dsm_file.file.read())  # readable() attribute on SpooledTemporaryFile which UploadFile
            tmp_csv.seek(
                0)  # is an alias for. PR is accepted for python v3.12, see https://github.com/python/cpython/pull/29560

            # This should hopefully open up the file for the processor.
            dsm = get_dsm_from_csv(tmp_csv)
            if dsm is None:
                raise e.DSMFileNotFoundException
        except Exception as exc:
            logger.debug(exc)
        finally:
            tmp_csv.close()
    else:
        raise e.DSMFileNotFoundException

    return dsm


def run_simulation(db_connection: PooledMySQLConnection, sim_settings: models.EditSimSettings,
                   vcs_ids: List[int],
                   design_group_ids: List[int], user_id, is_monte_carlo: bool = False, normalized_npv: bool = False
                   ) -> List[models.Simulation]:
    design_results = []

    if not check_sim_settings(sim_settings):
        raise e.BadlyFormattedSettingsException
    interarrival = sim_settings.interarrival_time
    flow_time = sim_settings.flow_time
    runtime = sim_settings.end_time - sim_settings.start_time
    non_tech_add = sim_settings.non_tech_add
    discount_rate = sim_settings.discount_rate
    process = sim_settings.flow_process
    time_unit = TIME_FORMAT_DICT.get(sim_settings.time_unit)
    runs = sim_settings.runs

    all_sim_data = get_all_sim_data(db_connection, vcs_ids, design_group_ids)

    all_market_values = get_all_market_values(db_connection, vcs_ids)

    all_designs = get_all_designs(db_connection, design_group_ids)

    all_vd_design_values = get_all_vd_design_values(db_connection, [design.id for design in all_designs])

    all_dsm_ids = life_cycle_storage.get_multiple_dsm_file_id(db_connection, vcs_ids)

    for vcs_id in vcs_ids:
        market_values = [mi for mi in all_market_values if mi['vcs'] == vcs_id]
        dsm_id = [dsm for dsm in all_dsm_ids if dsm[0] == vcs_id]
        dsm = None
        if len(dsm_id) > 0:
            dsm = get_dsm_from_file_id(db_connection, dsm_id[0][1], user_id)
        for design_group_id in design_group_ids:
            sim_data = [sd for sd in all_sim_data if sd['vcs'] == vcs_id and sd['design_group'] == design_group_id]
            if sim_data is None or sim_data == []:
                raise e.VcsFailedException

            if not check_entity_rate(sim_data, process):
                raise e.RateWrongOrderException

            designs = [design.id for design in all_designs if design.design_group_id == design_group_id]

            if designs is None or []:
                raise e.DesignIdsNotFoundException

            for design in designs:
                vd_values = [vd for vd in all_vd_design_values if vd['design'] == design]
                processes, non_tech_processes = populate_processes(non_tech_add, sim_data, design, market_values,
                                                                   vd_values)

                if dsm is None:
                    dsm = create_simple_dsm(processes)

                logger.debug(f'DSM: {dsm}')

                sim = des.Des()

                try:
                    if is_monte_carlo:
                        results = sim.run_parallell_simulations(flow_time, interarrival, process, processes,
                                                                non_tech_processes,
                                                                non_tech_add, dsm, time_unit, discount_rate, runtime,
                                                                runs)
                    else:
                        results = sim.run_simulation(flow_time, interarrival, process, processes, non_tech_processes,
                                                     non_tech_add, dsm, time_unit,
                                                     discount_rate, runtime)

                except Exception as exc:
                    tb = sys.exc_info()[2]
                    logger.debug(
                        f'{exc.__class__}, {exc}, {exc.with_traceback(tb)}')
                    print(f'{exc.__class__}, {exc}')
                    raise e.SimulationFailedException

                sim_res = models.Simulation(
                    time=results.timesteps[-1],
                    mean_NPV=results.normalize_npv() if normalized_npv else results.mean_npv(),
                    max_NPVs=results.all_max_npv(),
                    mean_payback_time=results.mean_npv_payback_time(),
                    all_npvs=results.npvs
                )

                design_results.append(sim_res)
    logger.debug('Returning the results')
    return design_results


def populate_processes(non_tech_add: NonTechCost, db_results, design: int,
                       mi_values=None,
                       vd_values=None):
    if mi_values is None:
        mi_values = []
    nsp = NumericStringParser()

    technical_processes = []
    non_tech_processes = []

    for row in db_results:
        vd_values_row = [vd for vd in vd_values if vd['vcs_row'] == row['id'] and vd['design'] == design]
        if row['category'] != 'Technical processes':
            try:
                non_tech = models.NonTechnicalProcess(
                    cost=nsp.eval(parse_formula(row['cost'], vd_values_row, mi_values)),
                    revenue=nsp.eval(
                        parse_formula(row['revenue'], vd_values_row, mi_values)),
                    name=row['iso_name'])
            except Exception as exc:
                logger.debug(f'{exc.__class__}, {exc}')
                raise e.FormulaEvalException(row['id'])
            non_tech_processes.append(non_tech)

        elif row['iso_name'] is not None and row['sub_name'] is None:
            try:
                time = nsp.eval(parse_formula(
                    row['time'], vd_values, mi_values))
                cost_formula = parse_formula(row['cost'], vd_values, mi_values)
                revenue_formula = parse_formula(
                    row['revenue'], vd_values, mi_values)
                p = Process(row['id'],
                            time,
                            nsp.eval(expr.replace_all(
                                'time', time, cost_formula)),
                            nsp.eval(expr.replace_all(
                                'time', time, revenue_formula)),
                            row['iso_name'], non_tech_add, TIME_FORMAT_DICT.get(
                        row['time_unit'].lower())
                            )
                if p.time < 0:
                    raise e.NegativeTimeException(row['id'])
            except Exception as exc:
                logger.debug(f'{exc.__class__}, {exc}')
                raise e.FormulaEvalException(row['id'])
            technical_processes.append(p)
        elif row['sub_name'] is not None:
            try:
                time = nsp.eval(parse_formula(
                    row['time'], vd_values, mi_values))
                cost_formula = parse_formula(row['cost'], vd_values, mi_values)
                revenue_formula = parse_formula(
                    row['revenue'], vd_values, mi_values)
                p = Process(row['id'],
                            time,
                            nsp.eval(expr.replace_all(
                                'time', time, cost_formula)),
                            nsp.eval(expr.replace_all(
                                'time', time, revenue_formula)),
                            row['sub_name'], non_tech_add, TIME_FORMAT_DICT.get(
                        row['time_unit'].lower())
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


def get_sim_data(db_connection: PooledMySQLConnection, vcs_id: int, design_group_id: int):
    query = f'SELECT cvs_vcs_rows.id, cvs_vcs_rows.iso_process, cvs_iso_processes.name as iso_name, category, \
            subprocess, cvs_subprocesses.name as sub_name, time, time_unit, cost, revenue, rate FROM cvs_vcs_rows \
            LEFT OUTER JOIN cvs_subprocesses ON cvs_vcs_rows.subprocess = cvs_subprocesses.id \
            LEFT OUTER JOIN cvs_iso_processes ON cvs_vcs_rows.iso_process = cvs_iso_processes.id \
                OR cvs_subprocesses.iso_process = cvs_iso_processes.id \
            LEFT OUTER JOIN cvs_design_mi_formulas ON cvs_vcs_rows.id = cvs_design_mi_formulas.vcs_row \
            WHERE cvs_vcs_rows.vcs = %s AND cvs_design_mi_formulas.design_group = %s ORDER BY `index`'
    with db_connection.cursor(prepared=True) as cursor:
        cursor.execute(query, [vcs_id, design_group_id])
        res = cursor.fetchall()
        res = [dict(zip(cursor.column_names, row)) for row in res]
    return res


def get_all_sim_data(db_connection: PooledMySQLConnection, vcs_ids: List[int], design_group_ids: List[int]):
    try:
        query = f'SELECT cvs_vcs_rows.id, cvs_vcs_rows.vcs, cvs_design_mi_formulas.design_group, \
                    cvs_vcs_rows.iso_process, cvs_iso_processes.name as iso_name, category, \
                    subprocess, cvs_subprocesses.name as sub_name, time, time_unit, cost, revenue, rate FROM cvs_vcs_rows \
                    LEFT OUTER JOIN cvs_subprocesses ON cvs_vcs_rows.subprocess = cvs_subprocesses.id \
                    LEFT OUTER JOIN cvs_iso_processes ON cvs_vcs_rows.iso_process = cvs_iso_processes.id \
                        OR cvs_subprocesses.iso_process = cvs_iso_processes.id \
                    LEFT OUTER JOIN cvs_design_mi_formulas ON cvs_vcs_rows.id = cvs_design_mi_formulas.vcs_row \
                    WHERE cvs_vcs_rows.vcs IN ({",".join(["%s" for _ in range(len(vcs_ids))])}) \
                    AND cvs_design_mi_formulas.design_group \
                    IN ({",".join(["%s" for _ in range(len(design_group_ids))])}) ORDER BY `index`'
        with db_connection.cursor(prepared=True) as cursor:
            cursor.execute(query, vcs_ids + design_group_ids)
            res = cursor.fetchall()
            res = [dict(zip(cursor.column_names, row)) for row in res]
    except Error as error:
        logger.debug(f'Error msg: {error.msg}')
        raise e.CouldNotFetchSimulationDataException
    return res


def get_vd_design_values(db_connection: PooledMySQLConnection, vcs_row_id: int,
                         design: int) -> List[ValueDriverDesignValue]:
    select_statement = MySQLStatementBuilder(db_connection)
    res = select_statement \
        .select('cvs_vd_design_values', ['cvs_value_drivers.id', 'design', 'name', 'value', 'unit']) \
        .inner_join('cvs_value_drivers', 'cvs_vd_design_values.value_driver = cvs_value_drivers.id') \
        .inner_join('cvs_vcs_need_drivers', 'cvs_vcs_need_drivers.value_driver = cvs_value_drivers.id') \
        .inner_join('cvs_stakeholder_needs', 'cvs_stakeholder_needs.id = cvs_vcs_need_drivers.stakeholder_need') \
        .where('vcs_row = %s and design = %s', [vcs_row_id, design]) \
        .execute(fetch_type=FetchType.FETCH_ALL, dictionary=True)

    logger.debug(f'Fetched {len(res)} value driver design values')
    return res


def get_all_vd_design_values(db_connection: PooledMySQLConnection, designs: List[int]):
    try:
        query = f'SELECT cvs_value_drivers.id, design, name, value, unit, vcs_row \
                        FROM cvs_vd_design_values \
                        INNER JOIN cvs_value_drivers ON cvs_vd_design_values.value_driver = cvs_value_drivers.id \
                        INNER JOIN cvs_vcs_need_drivers ON cvs_vcs_need_drivers.value_driver = cvs_value_drivers.id \
                        INNER JOIN cvs_stakeholder_needs ON cvs_stakeholder_needs.id = cvs_vcs_need_drivers.stakeholder_need \
                        WHERE design IN ({",".join(["%s" for _ in range(len(designs))])})'
        with db_connection.cursor(prepared=True) as cursor:
            cursor.execute(query, designs)
            res = cursor.fetchall()
            res = [dict(zip(cursor.column_names, row)) for row in res]
    except Error as error:
        logger.debug(f'Error msg: {error.msg}')
        raise e.CouldNotFetchValueDriverDesignValuesException
    return res


def get_simulation_settings(db_connection: PooledMySQLConnection, project_id: int):
    logger.debug(f'Fetching simulation settings for project {project_id}')

    select_statement = MySQLStatementBuilder(db_connection)
    res = select_statement.select(SIM_SETTINGS_TABLE, SIM_SETTINGS_COLUMNS) \
        .where('project = %s', [project_id]) \
        .execute(fetch_type=FetchType.FETCH_ONE, dictionary=True)

    if res is None:
        raise e.SimSettingsNotFoundException

    return populate_sim_settings(res)


def edit_simulation_settings(db_connection: PooledMySQLConnection, project_id: int,
                             sim_settings: models.EditSimSettings):
    logger.debug(f'Editing simulation settings for project {project_id}')

    if (sim_settings.flow_process is None and sim_settings.flow_start_time is None) \
            or (sim_settings.flow_process is not None and sim_settings.flow_start_time is not None):
        raise e.InvalidFlowSettingsException

    count_sim = MySQLStatementBuilder(db_connection)
    count = count_sim.count(SIM_SETTINGS_TABLE) \
        .where('project = %s', [project_id]) \
        .execute(fetch_type=FetchType.FETCH_ONE, dictionary=True)

    count = count['count']
    logger.debug(count)

    if sim_settings.flow_process is not None:
        flow_process_exists = False
        vcss = vcs_storage.get_all_vcs(db_connection, project_id).chunk
        for vcs in vcss:
            rows = vcs_storage.get_vcs_table(db_connection, project_id, vcs.id)
            for row in rows:
                if (row.iso_process is not None and row.iso_process.name == sim_settings.flow_process) or \
                        (row.subprocess is not None and row.subprocess.name == sim_settings.flow_process):
                    flow_process_exists = True
                    break

        if not flow_process_exists:
            raise e.FlowProcessNotFoundException

    if (count == 1):
        columns = SIM_SETTINGS_COLUMNS[1:]
        set_statement = ','.join([col + ' = %s' for col in columns])

        values = [sim_settings.time_unit.value, sim_settings.flow_process, sim_settings.flow_start_time,
                  sim_settings.flow_time,
                  sim_settings.interarrival_time, sim_settings.start_time, sim_settings.end_time,
                  sim_settings.discount_rate, sim_settings.non_tech_add.value, sim_settings.monte_carlo,
                  sim_settings.runs]
        update_Statement = MySQLStatementBuilder(db_connection)
        _, rows = update_Statement \
            .update(table=SIM_SETTINGS_TABLE, set_statement=set_statement, values=values) \
            .where('project = %s', [project_id]) \
            .execute(return_affected_rows=True)

    elif (count == 0):
        create_sim_settings(db_connection, project_id, sim_settings)

    return True


def create_sim_settings(db_connection: PooledMySQLConnection, project_id: int,
                        sim_settings: models.EditSimSettings) -> bool:
    values = [project_id] + [sim_settings.time_unit.value, sim_settings.flow_process, sim_settings.flow_start_time,
                             sim_settings.flow_time,
                             sim_settings.interarrival_time, sim_settings.start_time, sim_settings.end_time,
                             sim_settings.discount_rate, sim_settings.non_tech_add.value, sim_settings.monte_carlo,
                             sim_settings.runs]

    insert_statement = MySQLStatementBuilder(db_connection)
    insert_statement.insert(SIM_SETTINGS_TABLE, SIM_SETTINGS_COLUMNS) \
        .set_values(values) \
        .execute(fetch_type=FetchType.FETCH_NONE)

    return True


def get_market_values(db_connection: PooledMySQLConnection, vcs: int):
    select_statement = MySQLStatementBuilder(db_connection)
    res = select_statement \
        .select('cvs_market_input_values', ['id', 'name', 'value', 'unit']) \
        .inner_join('cvs_market_inputs', 'cvs_market_input_values.market_input = cvs_market_inputs.id') \
        .where('vcs = %s', [vcs]) \
        .execute(fetch_type=FetchType.FETCH_ALL, dictionary=True)
    return res


def get_all_market_values(db_connection: PooledMySQLConnection, vcs_ids: List[int]):
    try:
        query = f'SELECT id, name, value, unit, vcs \
                FROM cvs_market_input_values \
                INNER JOIN cvs_market_inputs ON cvs_market_input_values.market_input = cvs_market_inputs.id \
                WHERE cvs_market_input_values.vcs IN ({",".join(["%s" for _ in range(len(vcs_ids))])})'
        with db_connection.cursor(prepared=True) as cursor:
            cursor.execute(query, vcs_ids)
            res = cursor.fetchall()
            res = [dict(zip(cursor.column_names, row)) for row in res]
    except Error as error:
        logger.debug(f'Error msg: {error.msg}')
        raise e.CouldNotFetchMarketInputValuesException
    return res


def parse_formula(formula: str, vd_values, mi_values) -> str:
    new_formula = formula
    vd_names = expr.get_prefix_variables('VD', new_formula)
    mi_names = expr.get_prefix_variables('EF', new_formula)

    for vd in vd_values:
        for name in vd_names:
            unit = vd["unit"] if vd["unit"] is not None and vd["unit"] != "" else "N/A"
            if name == f'{vd["name"]} [{unit}]':
                new_formula = expr.replace_prefix_variables("VD", name, str(vd["value"]), new_formula)
    for mi in mi_values:
        for name in mi_names:
            unit = mi["unit"] if mi["unit"] is not None and mi["unit"] != "" else "N/A"
            if name == f'{mi["name"]} [{unit}]':
                new_formula = expr.replace_prefix_variables("EF", name, str(mi["value"]), new_formula)
    new_formula = expr.remove_strings_replace_zero(new_formula)

    return new_formula


def check_entity_rate(db_results, flow_process_name: str):
    rate_check = True
    # Set the flow_process_index to be highest possible.
    flow_process_index = len(db_results)
    for i in range(len(db_results)):
        if db_results[i]['sub_name'] == flow_process_name or db_results[i]['iso_name'] == flow_process_name:
            flow_process_index = i

        if i > flow_process_index:
            for j in range(i, len(db_results)):
                if db_results[j]['rate'] == 'per_project' and db_results[j]['category'] == 'Technical processes':
                    print("Rate check false")
                    rate_check = False
                    break
            break

    return rate_check


def check_sim_settings(settings: models.EditSimSettings) -> bool:
    settings_check = True

    if settings.end_time - settings.start_time <= 0:
        settings_check = False

    if settings.flow_time > settings.end_time - settings.start_time:
        settings_check = False

    if settings.flow_start_time is not None and settings.flow_process is not None:
        settings_check = False

    if settings.flow_start_time is None and settings.flow_process is None:
        settings_check = False

    return settings_check


# Create DSM that only goes from one process to the other following the order of the index in the VCS
def create_simple_dsm(processes: List[Process]) -> dict:
    n = len(processes) + 2  # +2 for start and end
    dsm = dict()
    for i in range(n):
        if i == 0:
            name = "Start"
        elif i == n - 1:
            name = "End"
        else:
            name = processes[i - 1].name

        dsm.update({name: [1 if i + 1 == j else "X" if i == j else 0 for j in range(n)]})
    return dsm


def get_dsm_from_csv(path):
    try:
        pf = pd.read_csv(path)
    except Exception as e:
        logger.debug(f'{e.__class__}, {e}')

    dsm = dict()
    for v in pf.values:
        dsm.update({v[0]: v[1::].tolist()})

    return dsm


def get_dsm_from_file_id(db_connection: PooledMySQLConnection, file_id: int, user_id: int) -> dict:
    path = file_storage.db_get_file_path(db_connection, file_id, user_id)
    return get_dsm_from_csv(path.path)


def get_dsm_from_excel(path):
    pf = pd.read_excel(path)

    dsm = dict()
    for v in pf.values:
        dsm.update({v[0]: v[1::].tolist()})
    return dsm


def populate_sim_settings(db_result) -> models.SimSettings:
    logger.debug(f'Populating simulation settings')
    return models.SimSettings(
        project=db_result['project'],
        time_unit=db_result['time_unit'],
        flow_process=db_result['flow_process'],
        flow_start_time=db_result['flow_start_time'],
        flow_time=db_result['flow_time'],
        interarrival_time=db_result['interarrival_time'],
        start_time=db_result['start_time'],
        end_time=db_result['end_time'],
        discount_rate=db_result['discount_rate'],
        non_tech_add=db_result['non_tech_add'],
        monte_carlo=db_result['monte_carlo'],
        runs=db_result['runs']
    )

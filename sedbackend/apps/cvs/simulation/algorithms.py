import random
from typing import List

from mysql.connector.pooling import PooledMySQLConnection
from sedbackend.apps.cvs.vcs import storage as vcs_storage
from sedbackend.apps.cvs.simulation import models

import sedbackend.apps


class Simulation:
    def __init__(self, db_connection: PooledMySQLConnection, project_id: int, vcs_id: int, user_id: int):
        self.vcs_table_rows = vcs_storage.get_all_table_rows(db_connection, vcs_id, project_id, user_id)
        self.processes = populate_processes(db_connection, self.vcs_table_rows)
        self.dsm = create_dsm(self.processes)
        self.time = [0.0]
        self.cost = [0.0]
        self.revenue = [0.0]

    def to_run(self, row):
        return random.choices([i for i, _ in enumerate(row)], row, k=1)[0]

    def run(self, until) -> sedbackend.apps.cvs.simulation.models.Simulation:
        process_index = 0
        while self.time[-1] < until:
            process = self.processes[process_index]
            row = self.dsm[process_index]
            if self.time[-1] + process.time >= until:
                break
            self.time.append(process.time + self.time[-1])
            self.cost.append(process.cost + self.cost[-1])
            self.revenue.append(process.revenue + self.revenue[-1])
            if all(c == 0 for c in row):
                break
            process_index = self.to_run(row)
        sv = [self.revenue[i] - self.cost[i] for i in range(0, len(self.cost))]

        return sedbackend.apps.cvs.simulation.models.Simulation(
            time=self.time,
            surplus_values=sv,
            processes=self.processes
        )


def run_simulation(db_connection: PooledMySQLConnection, project_id: int, vcs_id: int, user_id: int,
                   time_interval: float) -> sedbackend.apps.cvs.simulation.models.Simulation:
    simulation = Simulation(db_connection, project_id, vcs_id, user_id)
    result = simulation.run(time_interval)
    return result


def populate_processes(db_connection: PooledMySQLConnection,
                       vcs_table_rows: List[sedbackend.apps.cvs.vcs.models.TableRowGet]) -> List[
    sedbackend.apps.cvs.simulation.models.Process]:
    processes = []

    for table_row in vcs_table_rows:
        if (table_row.iso_process and table_row.iso_process.category == 'Technical processes') \
                or (table_row.subprocess and table_row.subprocess.parent_process.category == 'Technical processes'):
            if table_row.iso_process:
                name = table_row.iso_process.name
            else:
                name = table_row.subprocess.name

            mi = sedbackend.apps.cvs.market_input.storage.get_market_input(db_connection, table_row.node_id)
            process = sedbackend.apps.cvs.simulation.models.Process(
                name=name,
                time=mi.time,
                cost=mi.cost,
                revenue=mi.revenue
            )
            processes.append(process)

    return processes


def create_dsm(processes: List[sedbackend.apps.cvs.simulation.models.Process]):
    dsm = empty_dsm(len(processes))
    for i in range(len(dsm) - 1):
        dsm[i][i + 1] = 1.0
    return dsm


def empty_dsm(length):
    matrix = [0] * length
    for i in range(len(matrix)):
        matrix[i] = [0] * length
    return matrix

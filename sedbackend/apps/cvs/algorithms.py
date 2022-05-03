import matplotlib.pyplot as plt
import random
import sedbackend.apps.cvs.models as models
from typing import List
from mysql.connector.pooling import PooledMySQLConnection
import sedbackend.apps.cvs.storage as storage


class Process:
    def __init__(self, time, cost, revenue, name):
        self.revenue = revenue
        self.cost = cost
        self.time = time
        self.name = name


class Simulation:
    def __init__(self, db_connection: PooledMySQLConnection, project_id: int, vcs_id: int, user_id: int):
        self.bpmn = storage.get_bpmn(db_connection, vcs_id, project_id, user_id)
        self.nodes: List[models.NodeGet] = self.bpmn.nodes
        self.edges: List[models.EdgeGet] = self.bpmn.edges
        self.dsm = createDSM(self.nodes, self.edges)
        self.processes = populate_processes(db_connection, self.nodes)
        self.time = [0.0]
        self.cost = [0.0]
        self.revenue = [0.0]

    def to_run(self, row):
        return random.choices([i for i, _ in enumerate(row)], row, k=1)[0]

    def run(self, until) -> models.Simulation:
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
        #plt.plot(self.time, sv)
        #plt.show()

        return models.Simulation(
            time_interval=self.time,
            surplus_values=sv,
            processes=self.processes
        )


p1 = Process(10, 100, 0, "Design")
p2 = Process(40, 80, 0, "Manufacturing")
p3 = Process(200, 20, 600, "Operation")
p4 = Process(10, 40, 0, "Maintenance")
p5 = Process(1, 0, 0, "Disposal")

_processes = [p1, p2, p3, p4, p5]
_dsm = [[0, 1, 0, 0, 0],
        [0, 0, 1, 0, 0],
        [0, 0, 0, 1, 0],
        [0, 0, 0.8, 0, 0.2],
        [0, 0, 0, 0, 0]]

#simulation = Simulation(_processes, _dsm)
#simulation.run(3000)


# ======================================================================================================================
# Simulation
# ======================================================================================================================

def run_simulation(db_connection: PooledMySQLConnection, project_id: int, vcs_id: int, user_id: int,
                   time_interval: float) -> models.Simulation:
    simulation = Simulation(db_connection, project_id, vcs_id, user_id)
    result = simulation.run(time_interval)
    return result


def populate_processes(db_connection: PooledMySQLConnection, nodes: List[models.NodeGet]) -> List[models.Process]:
    processes = []

    for node in nodes:
        mi = storage.get_market_input(db_connection, node.vcs_table_row.id)
        process = models.Process(
            name=node.name,
            time=mi.time,
            cost=mi.cost,
            revenue=mi.revenue
        )
        processes.append(process)

    return processes


# ======================================================================================================================
# Design Structure Matrix
# ======================================================================================================================

def createDSM(nodes: List[models.NodeGet], edges: List[models.EdgeGet]):
    dsm = emptyDSM(len(nodes))

    populateDSM(dsm, nodes, edges)

    return dsm

def emptyDSM(length):
    matrix = [0] * length
    for i in range(len(matrix)):
        matrix[i] = [0] * length
    return matrix

def populateDSM(DSM, nodes: List[models.NodeGet], edges: List[models.EdgeGet]):
    for e in edges:
        DSMfrom = nodes.index(e.from_node)
        DSMto = nodes.index(e.to_node)
        DSM[DSMfrom][DSMto] = e.probability
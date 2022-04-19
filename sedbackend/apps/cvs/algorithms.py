import simpy
import matplotlib.pyplot as plt
import random


class Process:
    def __init__(self, time, cost, revenue, name):
        self.revenue = revenue
        self.cost = cost
        self.time = time
        self.name = name


class Simulation:
    def __init__(self, processes, dsm):
        self.processes = processes
        self.dsm = dsm
        self.time = [0]
        self.cost = [0]
        self.revenue = [0]

    def to_run(self, row):
        return random.choices([i for i, _ in enumerate(row)], row, k=1)[0]

    def run(self, until):
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
        plt.plot(self.time, sv)
        plt.show()


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

simulation = Simulation(_processes, _dsm)
simulation.run(3000)

# Std imports
import numbers
import operator

import simpy
import numpy as np
from functools import reduce
from matplotlib import pyplot
from models import TableRowGet
from models import VCSISOProcess


class MockProcess:
    def __init__(self, name, time, cost, revenue):
        self.name = name
        self.time = time
        self.cost = cost
        self.revenue = revenue
        self.W = 1  # work to be completed, 1 means that 100 % of the activity remains
        self.WN = False  # " work now", work is not completed when initialized


class SimProcess:
    def __init__(self, p: MockProcess, children):
        self.p = p
        self.children = children


A = MockProcess("Design", time=300, cost=20, revenue=0)
B = MockProcess("Launch", time=50, cost=100, revenue=10)
C = MockProcess("Orbit", time=1000, cost=300, revenue=700)
D = MockProcess("Maintenance", time=300, cost=20, revenue=0)

_processes = [A, B, C, D]
_dsm = [[0, 1, 0, 0],
        [0, 0, 1, 0],
        [0, 0, 0, 1],
        [0, 0, 0, 0]]


class Simulation:
    def __init__(self, processes, dsm):
        self.processes = processes
        self.dsm = dsm
        self.sequence = self.transform()
        self.times = []
        self.costs = []
        self.revenues = []

    def transform(self):
        sequence = []
        for i, row in enumerate(self.dsm):
            children = []
            for j, cell in enumerate(row):
                if cell != 0:
                    children.append(self.processes[j])
            sequence.append(SimProcess(self.processes[i], children))
        return sequence

    def run_process(self, process: MockProcess):
        self.times.append(process.time)
        self.costs.append(process.cost)
        self.revenues.append(process.cost)

    def run(self):
        self.run_process(self.processes[0])
        for i, row in enumerate(self.dsm):
            for j, cell in enumerate(row):
                if cell == 1:
                    self.run_process(self.processes[j])
        print(self.times)
        print(self.costs)
        print(self.revenues)


sim = Simulation(_processes, _dsm)
sim.run()

# total_cost = []
# total_revenue = []
# total_time = []
# acc_time = [0]
# acc_sv = [0]
#
#
# def runProcess(process: MockProcess):
#    global total_time
#    global total_cost
#    global total_revenue
#    global acc_time
#    global acc_sv
#    if len(process.subprocesses):
#        print ("Running subprocesses of " + process.name)
#        for process in process.subprocesses:
#            runProcess(process)
#        print ("-------")
#    else:
#        print("Running " + process.name + " takes " + str(process.time))
#        total_time.append(process.time)
#        total_revenue.append(process.revenue)
#        total_cost.append(process.cost)
#        acc_time.append(process.time + acc_time[-1])
#        acc_sv.append(process.revenue - process.cost + acc_sv[-1])
#
#
# def run():
#    runProcess(processes[0])
#    for i, row in enumerate(dsm):
#        for j, cell in enumerate(row):
#            if cell == 1:
#                runProcess(processes[j])
#
#    time = reduce(operator.add, total_time, 0)
#    cost = reduce(operator.add, total_cost, 0)
#    revenue = reduce(operator.add, total_revenue, 0)
#
#    print("the total time is " + str(time))
#    print("the total cost is " + str(cost))
#    print("the total revenue is " + str(revenue))
#    acc_time.pop(0)
#    acc_sv.pop(0)
#    pyplot.plot(acc_time, acc_sv)
#    pyplot.show()
#
#
# run()

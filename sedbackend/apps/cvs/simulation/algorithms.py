import random as r
import numpy as np
from typing import List, Optional, Tuple
import simpy
import pandas as pd

from enum import Enum
from mysql.connector.pooling import PooledMySQLConnection

import models as sim_models
from sedbackend.apps.cvs.market_input.models import MarketInputGet
import sedbackend.apps.cvs.vcs.implementation as vcs_impl
import sedbackend.apps.cvs.market_input.implementation as mi_impl
from sedbackend.apps.cvs.vcs.models import VcsRow

TIMESTEP = 0.25

class TimeFormat(Enum):
    """
    The timeformats that can be chosen for a process. The values are the defaults for the
    simulation (years)
    """
    HOUR = 365*24
    DAY = 365
    WEEK = 52
    MONTH = 12
    YEAR = 1


class Simulation(object):
    #@param:
    #flow_time = the time that entities will flow in the system
    #interarrival_time = the rate at which entities will flow in the system
    #interarrival_process = the process at which the entities will start flowing
    #until = the total simulation time
    def __init__(self, flow_time, interarrival_time, interarrival_process, until, discount_rate, processes, non_tech_processes, dsm) -> None:
        self.flow_time = flow_time
        self.interarrival_time = interarrival_time
        self.interarrival_process = interarrival_process
        self.until = until
        self.discount_rate = discount_rate
        self.cum_NPV = [0]
        self.time_steps = [0]
        self.entities = []
        self.processes = processes 
        self.dsm_before_flow, self.dsm_after_flow = self.get_dsm_separation(dsm)

        """
        self.dsm = dict({'A': [0, 0, 0, 0], 
                         'B': [0, 0, 0.2, 0.8], 
                        'C': [0, 0, 0, 0], 
                        'D': [0, 0, 0, 0]}) 
                        #Cannot have rework here - since it will cause the work vector to go bananas
                        #'D': [1, 0, 0, 1]
        """
    #This method sets up the simpy environment and runs the simulation
    def run_simulation(self):
        env = simpy.Environment()
        env.process(self.lifecycle(env))
        env.process(self.observe_costs(env))
        env.run(until=self.until)
        #print([(e.total_cost, e.total_revenue) for e in self.entities])
    
    #Initializes the lifecycle in each of the entities. Runs everything before the interarrival
    #process as a single entity. R
    def lifecycle(self, env):
        e = Entity(env, self.processes)
        self.entities.append(e)
        yield env.process(e.lifecycle(self.dsm_before_flow, [self.processes[0]]))
        
        end_flow = env.now + self.flow_time
        while env.now < end_flow:
            yield env.timeout(self.generate_interarrival())
        
            e = Entity(env, self.processes)
            env.process(e.lifecycle(self.dsm_after_flow, [self.interarrival_process]))
            self.entities.append(e)
            
    #Observes the total time, cost, revenue, and NPV for each entity in each timestep. 
    def observe_costs(self, env):
        total_costs = [0]
        total_revenue = [0]
        

        while True:
            # print([f'cost: {e.cost}' for e in self.entities])
            #print([f'revenue: {e.revenue}' for e in self.entities])
            #print(f'Time: {env.now}')
            self.add_static_costs_to_entities()
            total_costs.append(sum([e.cost for e in self.entities]))
            total_revenue.append(sum([e.revenue for e in self.entities]))
            self.time_steps.append(env.now)


            self.calculate_NPV(total_costs, total_revenue, self.time_steps)
           # print(f'Time: {env.now}, total_cost: {sum([e.cost for e in self.entities])}, total_revenue: {sum([e.revenue for e in self.entities])}, cum_NPV: {self.cum_NPV}')
            yield env.timeout(TIMESTEP)


    #Generates the waiting time as interarrival rate on an exponential distribution
    def generate_interarrival(self):
        return np.random.exponential(self.interarrival_time)


    def add_static_costs_to_entities(self): #Adds the costs of the non-technical processes to all active entities. 
        for e in self.entities:
            e.cost += self.static_processes_costs / (len(self.entities) * self.until) #This works in the margin of 0.00000002 euros

    def calculate_NPV(self, total_costs, total_revenue, time_steps):
        timestep_revenue = total_revenue[len(time_steps) -1] - total_revenue[len(time_steps) - 2]
        timestep_cost = total_costs[len(time_steps) - 1] - total_costs[len(time_steps) - 2]

        net_revenue = timestep_revenue - timestep_cost #Cashflow for the timestep
        npv = net_revenue / ((1 + 0.08) ** time_steps[-1])
        self.cum_NPV.append(self.cum_NPV[-1] + npv)

    #Separates the given DSM into two dictionaries with the before flow and after flow parts of the dsm
    def get_dsm_separation(self, dsm):
        before_dsm = dict()
        dsm = dsm.copy()
        for p in self.processes:
            if p.name == self.interarrival_process.name:
                break
            before_dsm.update({p.name: dsm.pop(p.name)})
        return before_dsm,dsm


    """    
    def get_dsm_before_flow(self): #Example DSM
        return dict({'A': [0, 0, 0, 0]})

    def get_dsm_after_flow(self): #Example DSM
        return dict({'B': [0, 0, 0.2, 0.8], 
                    'C': [0, 0, 0, 0], 
                    'D': [0, 0, 0, 0]})
    """

class Entity(object):
    #@param
    #env = the simpy environment
    #processes = the processes that the entity will go through
    def __init__(self, env, processes) -> None:
        self.env = env
        self.processes = processes
        self.total_time = [0]
        self.total_cost = [0]
        self.total_revenue = [0]
    
    #Runs the lifecycle for this entity. 
    #Can choose between processes but cannot run multiple processes in parallell
    def lifecycle(self, dsm, current_processes):
        active_activities = current_processes
        while len(active_activities) > 0:
            print(f'curr time {self.env.now}')
            min_time = active_activities[0].time #For yielding in case there are multiple processes running in parallell
            for activity in active_activities:
                self.env.process(activity.run_process(self.env, self.total_cost, self.total_revenue))
                if activity.time < min_time:
                    min_time = activity.time
            
            start_time = self.env.now
            yield self.env.timeout(min_time)
       
            for activity in active_activities: #This loop is probably unneccessary since we do not check W anywhere atm
                if activity.W > 0:
                    activity.W = (self.env.now - start_time) / activity.time
            active_activities = self.find_active_activities(dsm, active_activities) #Find subsequent activities
    
    #Finds the active processes for the lifecycle based on the dsm and the current state
    #That the lifecycle is in. 
    def find_active_activities(self, dsm: dict, current_processes):
        active_activities = []
        for process in current_processes:
            if(process.name not in dsm.keys()):
                break

            transitions = dsm.get(process.name)
            
            if(all([p==0 for p in transitions])): #Checks if all rows are 0, if that is the case then there is nothing more to be done after this process 
                continue

            process_index = self.choose_process_from_row(transitions) #Select the process index from its row
            active_activities.append(self.processes[process_index]) 
                 
        return active_activities
    
    #Selects a process index from a row of transitional probabilities
    def choose_process_from_row(self, row):
        return r.choices([i for i,_ in enumerate(row)], row, k=1)[0]


class Process(object):
    #@param
    #time = the time a process will take in years. 
    #cost = the cost of a process
    #revenue = the revenue of a process
    #name = the name of a process
    #time_format = the unit in which the time is given. 
    def __init__(self, time, cost, revenue, name, time_format: Optional[TimeFormat] = None) -> None:
        self.time = self.convert_time_format_to_default(time, time_format)
        self.cost = cost
        self.revenue = revenue
        self.W = 1
        self.WN = False
        self.name = name
    
    #Converts all times to the correct (default: Years) time format
    def convert_time_format_to_default(self, time, time_format: Optional[TimeFormat] = None):
        return (time / time_format.value) if time_format is not None else 0

    #Runs a process and adds the cost and the revenue to the entity
    def run_process(self, env, total_cost, total_revenue):
        #print(f'Started working on process: {self.name}')
        yield env.timeout(self.time * self.W)
        #print(f'Time after step in lifecycle: {env.now}')
        total_cost.append(total_cost[-1] + self.cost)
        total_revenue.append(total_revenue[-1] + self.revenue)
        self.W = 0


def run_simulation(db_connection: PooledMySQLConnection, vcs_id: int, flow_time: int, 
        interarrival_time: float, pid: int, time_interval: float, discount_rate: float,
        user_id: int) -> sim_models.Simulation:
    
    #pid is a processid which means that we need to fetch the processes first. 
    vcs_rows = vcs_impl.get_vcs_table(vcs_id, user_id)
    market_input = mi_impl.get_all_market_inputs(vcs_id, user_id)

    #BUG entering pid as param to the Simulation. Will fail on the separate dsm method since that one wants an actual process. (or a name)
    sim = Simulation(flow_time, interarrival_time, pid, time_interval, discount_rate, populate_processes(vcs_rows, market_input), populate_non_tech_processes(vcs_rows, market_input))
    sim.run_simulation()

    return sim_models.Simulation(
        time=sim.time_steps,
        cumulative_NPV=sim.cum_NPV,
        processes=sim.processes
    )


def populate_processes(vcs_rows: List[VcsRow], market_input: List[MarketInputGet]) -> List[sim_models.Process]:
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

def populate_non_tech_processes(vcs_rows: List[VcsRow], market_input: List[MarketInputGet]) -> List[sim_models.NonTechnicalProcess]:
    non_tech_processes = []
    for row in vcs_rows:
        if (row.iso_process and row.iso_process.category is not 'Technical processes') \
            or (row.subprocess and row.subprocess.parent_process.category is not 'Techical processes'):
                if row.iso_process:
                    name = row.iso_process.name
                else: 
                    name = row.subprocess.name
            
                for mi in market_input:
                    if mi.vcs_row == row.id:
                        non_tech_process = sim_models.NonTechnicalProcess(
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
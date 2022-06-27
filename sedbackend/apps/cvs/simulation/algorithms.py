import random as r
import numpy as np
from typing import List
import simpy

from mysql.connector.pooling import PooledMySQLConnection

import sedbackend.apps
TIMESTEP = 1


def run_simulation(db_connection: PooledMySQLConnection, project_id: int, vcs_id: int, user_id: int, #Old code, needs rework
                   time_interval: float) -> sedbackend.apps.cvs.simulation.models.Simulation:
    simulation = Simulation(db_connection, project_id, vcs_id, user_id)
    result = simulation.run(time_interval)
    return result


def populate_processes(db_connection: PooledMySQLConnection, #Old code, needs rework
                       vcs_table_rows: List[sedbackend.apps.cvs.vcs.models.VcsRow]) -> List[
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

class Simulation(object):
    #@param:
    #flow_time = the time that entities will flow in the system
    #interarrival_time = the rate at which entities will flow in the system
    #interarrival_process = the process at which the entities will start flowing
    #until = the total simulation time
    def __init__(self, flow_time, interarrival_time, interarrival_process, until) -> None:
        self.flow_time = flow_time
        self.interarrival_time = interarrival_time
        self.interarrival_process = interarrival_process
        self.until = until
        self.entities = []
        self.processes = populate_processes()
        self.dsm = dict({'A': [0, 0, 0, 0], 
                         'B': [0, 0, 0.2, 0.8], 
                        'C': [0, 0, 0, 0], 
                        'D': [0, 0, 0, 0]}) 
                        #Cannot have rework here - since it will cause the work vector to go bananas
                        #'D': [1, 0, 0, 1]
    
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
        yield env.process(e.lifecycle(self.get_dsm_before_flow(), [self.processes[0]]))
        
        end_flow = env.now + self.flow_time
        while env.now < end_flow:
            yield env.timeout(self.generate_interarrival())
        
            e = Entity(env, self.processes)
            env.process(e.lifecycle(self.get_dsm_after_flow(), [self.interarrival_process]))
            self.entities.append(e)
            
    #Observes the total time, cost, and revenue for each entity in each timestep. 
    def observe_costs(self, env):
        while True:
            print([f'cost: {e.total_cost[-1]}' for e in self.entities])
            print([f'revenue: {e.total_revenue[-1]}' for e in self.entities])
            print(f'Time: {env.now}')
            print(f'Time: {env.now}, total_cost: {sum([e.total_cost[-1] for e in self.entities])}, total_revenue: {sum([e.total_revenue[-1] for e in self.entities])}')
            yield env.timeout(TIMESTEP)

    #Generates the waiting time as interarrival rate on an exponential distribution
    def generate_interarrival(self):
        return np.random.exponential(self.interarrival_time)
    
    def get_dsm_before_flow(self): #Example DSM
        return dict({'A': [0, 0, 0, 0]})

    def get_dsm_after_flow(self): #Example DSM
        return dict({'B': [0, 0, 0.2, 0.8], 
                    'C': [0, 0, 0, 0], 
                    'D': [0, 0, 0, 0]})

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
    #time = the time a process will take
    #cost = the cost of a process
    #revenue = the revenue of a process
    #name = the name of a process
    def __init__(self, time, cost, revenue, name) -> None:
        self.time = time
        self.cost = cost
        self.revenue = revenue
        self.W = 1
        self.WN = False
        self.name = name
    
    #Runs a process and adds the cost and the revenue to the entity
    def run_process(self, env, total_cost, total_revenue):
        print(f'Started working on process: {self.name}')
        yield env.timeout(self.time * self.W)
        print(f'Time after step in lifecycle: {env.now}')
        total_cost.append(total_cost[-1] + self.cost)
        total_revenue.append(total_revenue[-1] + self.revenue)
        self.W = 0
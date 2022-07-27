import random as r
import numpy as np
from typing import List, Optional, Tuple
import simpy
import pandas as pd

from enum import Enum


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
    def __init__(self, flow_time, flow_rate, flow_process, simulation_runtime, discount_rate, processes, non_tech_processes, dsm) -> None:
        self.flow_time = flow_time
        self.interarrival_time = flow_rate
        self.interarrival_process = flow_process
        self.until = simulation_runtime
        self.discount_rate = discount_rate
        self.cum_NPV = [0]
        self.time_steps = [0]
        self.entities = []
        self.processes = processes 
        self.non_tech_costs = sum([p.cost for p in non_tech_processes])
        self.non_tech_revenues = sum([p.revenue for p in non_tech_processes])
        self.dsm_before_flow, self.dsm_after_flow = self.get_dsm_separation(dsm)
        r.seed(0) #Remove for production
        np.random.seed(0) #Remove for production

    #This method sets up the simpy environment and runs the simulation
    def run_simulation(self):
        env = simpy.Environment()
        env.process(self.lifecycle(env))
        env.process(self.observe_costs(env))
        env.run(until=self.until)
    
    #Initializes the lifecycle in each of the entities. Runs everything before the interarrival
    #process as a single entity. R
    def lifecycle(self, env):
        total_ent_amount = (1 / self.interarrival_time) * self.flow_time

        e = Entity(env, self.processes, self.non_tech_costs)
        self.entities.append(e)
        yield env.process(e.lifecycle(self.dsm_before_flow, [self.processes[0]], 1))
        
        end_flow = env.now + self.flow_time
        while env.now < end_flow:
            yield env.timeout(self.generate_interarrival())
        
            e = Entity(env, self.processes, self.non_tech_costs)
            self.entities.append(e)
            env.process(e.lifecycle(self.dsm_after_flow, [self.interarrival_process], total_ent_amount))
        
        print('Done')
            
            
    #Observes the total time, cost, revenue, and NPV for each entity in each timestep. 
    def observe_costs(self, env): #TODO fix calculation of NPV. Currently it's bonkers
        total_costs = [0]
        total_revenue = [0]

        while True:
          
            #self.add_static_costs_to_entities()
            
            #total_costs.append(sum([e.total_cost[-1] for e in self.entities]))
            #total_revenue.append(sum([e.total_revenue[-1] for e in self.entities]))
            
            total_costs.append(sum([e.cost for e in self.entities]))
            total_revenue.append(sum([e.revenue for e in self.entities]))
            self.time_steps.append(env.now)


            self.calculate_NPV(total_costs, total_revenue, self.time_steps)
            yield env.timeout(TIMESTEP)


    #Generates the waiting time as interarrival rate on an exponential distribution
    def generate_interarrival(self):
        return np.random.exponential(self.interarrival_time)


    #def add_static_costs_to_entities(self): #Adds the costs of the non-technical processes to all active entities. 
    #    for e in self.entities:
    #        e.total_cost.append(e.total_cost[-1] + self.static_processes_costs * TIMESTEP/ (len(self.entities) * self.until))  #This works in the margin of 0.00000002 euros

    def calculate_NPV(self, total_costs, total_revenue, time_steps):
        timestep_revenue = total_revenue[len(time_steps) -1] - total_revenue[len(time_steps) - 2]
        timestep_cost = total_costs[len(time_steps) - 1] - total_costs[len(time_steps) - 2]
        #print(timestep_revenue, timestep_cost)

        net_revenue = timestep_revenue - timestep_cost #Cashflow for the timestep
        npv = net_revenue / ((1 + self.discount_rate) ** time_steps[-1])
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

class Entity(object):
    #@param
    #env = the simpy environment
    #processes = the processes that the entity will go through
    def __init__(self, env, processes, total_non_tech_costs) -> None:
        self.env = env
        self.processes = processes
        self.total_time = [0]
        self.total_cost = [0]
        self.total_revenue = [0]
        self.cost = 0
        self.revenue = 0
        self.total_non_tech_costs = total_non_tech_costs
    
    #Runs the lifecycle for this entity. 
    #Can choose between processes but cannot run multiple processes in parallell
    def lifecycle(self, dsm, current_processes, ent_amount):
        active_activities = current_processes
        while len(active_activities) > 0:
            #print(f'curr time {self.env.now}')
            min_time = active_activities[0].time #For yielding in case there are multiple processes running in parallell
            for activity in active_activities:
                self.env.process(activity.run_process(self.env, self, ent_amount, self.total_non_tech_costs))
                if activity.time < min_time:
                    min_time = activity.time
            
            #start_time = self.env.now
            yield self.env.timeout(min_time)
       
            #for activity in active_activities: #This loop is probably unneccessary since we do not check W anywhere atm
            #    if activity.W > 0:
            #        activity.W = (self.env.now - start_time) / activity.time
            active_activities = self.find_active_activities(dsm, active_activities) #Find subsequent activities

        print(f'Entity: {self} done, total time: {sum([p.time for p in self.processes])}')
    
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
    def __init__(self, time, cost, revenue, name, add_non_tech: bool, time_format: Optional[TimeFormat] = None) -> None:
        self.time = self.convert_time_format_to_default(time, time_format)
        self.cost = cost
        self.revenue = revenue
        self.W = 1
        self.WN = False
        self.name = name
        self.add_non_tech = add_non_tech
    
    #Converts all times to the correct (default: Years) time format
    def convert_time_format_to_default(self, time, time_format: Optional[TimeFormat] = None):
        return (time / time_format.value) if time_format is not None else 0

    #Runs a process and adds the cost and the revenue to the entity
    def run_process(self, env, entity, ent_amount, non_tech_costs):
        #print(f'Started working on process: {self.name}')
        yield env.timeout(self.time * self.W)
        #print(f'Time after step in lifecycle: {env.now}')
        #non_tech_costs = total_non_tech_cost * self.time / (process_time * amount_of_entities) #Add this to the total cost in order to add non tech costs to processes
        
        entity.cost += self.cost
        entity.revenue += self.revenue
        
        if self.add_non_tech:
            added_cost = non_tech_costs * self.time / (sum([p.time for p in entity.processes]) * ent_amount)
            entity.cost += added_cost

        #total_cost.append(total_cost[-1] + self.cost)
        #total_revenue.append(total_revenue[-1] + self.revenue)
        
        self.W = 0


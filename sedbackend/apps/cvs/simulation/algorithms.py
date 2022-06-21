import random
from typing import List
import simpy

from mysql.connector.pooling import PooledMySQLConnection
from sedbackend.apps.cvs.vcs import storage as vcs_storage
from sedbackend.apps.cvs.simulation import models

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


def create_dsm(processes: List[sedbackend.apps.cvs.simulation.models.Process]): #Old code. This simply creates a dsm with 1s down the diagonal. Needs to be reworked to fit with rework and multiple parallell processes
    dsm = empty_dsm(len(processes))
    for i in range(len(dsm) - 1):
        dsm[i][i + 1] = 1.0
    return dsm


def empty_dsm(length): #Old code. 
    matrix = [0] * length
    for i in range(len(matrix)):
        matrix[i] = [0] * length
    return matrix

class Simulation(object):
    def __init__(self, amount_of_entities, until) -> None:
        self.amount_of_entities = amount_of_entities
        self.until = until
        

    def run_simulation(self):
        i = 0
        entities = []
        env = simpy.Environment() #Simpy initialization
        while i < self.amount_of_entities: #Initializing the entities that are going to flow through the lifecycle. 
            entities.append(Entity(env))   #This should probs be changed to an interarrival time and some random values
            i += 1

        env.run(until=self.until)
        self.calculate(entities)

    def calculate(self, entities):
        print(f'Total cost: {sum([ent.total_cost[-1] for ent in entities])}')
        print(f'Total revenue: {sum([ent.total_revenue[-1] for ent in entities])}')
        print(f'Total time: {sum([ent.total_time[-1] for ent in entities])}')




class Entity(object):
    def __init__(self, env) -> None:
        self.env = env
        self.processes = [Process(env, 20, 20, 60, 'A'), Process(env, 5, 5, 15, 'B'), Process(env, 2,2,6, 'C'), Process(env, 14, 14, 42, 'D')] #Hard coded values for the processes
        self.action = env.process(self.lifecycle(self.create_DSM()))
        self.action = env.process(self.calculate_costs())
        self.total_time = []
        self.total_cost = []
        self.total_revenue = []
        self.time = 0
        self.cost = 0
        self.revenue = 0

    
    def run(self):
        for p in self.processes: #Just looping through all processes. Now we need to figure out how to ensure that they run in DSM order
                                 #Then we need to check for rework and add that to the processes in some way. 
                                 #We should be able to observe the total costs in some observe function i think
                                 #The question is how... Maybe start here
            print(f'process time: {p.time} ')
            print(f'Timestamp entering process: {self.env.now}')
            yield self.env.process(p.lifecycle(self))

            print(f'Timestamp after process: {self.env.now}')
        

    def lifecycle(self, dsm):
        #Kom på ett sätt att lista ut vilka aktiviteter som är aktiva!
        # - Typ linked list av aktiviteter?
        # - Eller via DSM
        
        active_activities = self.find_active_activities(dsm, None) #Find the first active activities
        while len(active_activities) > 0:
            min_time = active_activities[0].time
            for activity in active_activities:
                
                print(activity.name, activity.W)
               
                self.env.process(activity.lifecycle(self, self.cost, self.revenue))
                self.cost += activity.cost
                self.revenue += activity.revenue
                if activity.time < min_time:
                    min_time = activity.time
                

            start_time = self.env.now
            yield self.env.timeout(min_time)
            for activity in active_activities:
                if activity.W > 0:
                    activity.W = (self.env.now - start_time) / activity.time
            active_activities = self.find_active_activities(dsm, active_activities) #Find subsequent activities
             
    def calculate_costs(self):
        while True:
            self.total_time.append(self.env.now)
            self.total_cost.append(self.cost)
            self.total_revenue.append(self.revenue)
            yield self.env.timeout(TIMESTEP)

    
    def find_active_activities(self, dsm: dict, current_processes = None):
        if current_processes == None:
            return [self.processes[0]]
        else:
            active_activities = []
            for process in current_processes:
                indices = dsm.get(process.name)
                for i, w in enumerate(indices):
                    if w > 0 and self.processes[i].W > 0 and self.processes[i].name != process.name:
                        active_activities.append(self.processes[i])
            print(f'Active activities: {[a.name for a in active_activities]}')
            return active_activities
        

    def create_DSM(self): #Just an example - remove for production
        return dict({'A': [1, 0.3, 0, 0], 
                    'B': [0, 1, 1, 1], 
                    'C': [0, 0, 1, 0], 
                    'D': [1, 0, 0, 1]})

    def create_rework_DSM(self): #Just an example - remove for production
        return dict({
            'A': [0, 0.2, 0, 0],
            'B': [0, 0, 0, 0],
            'C': [0, 0, 0, 0],
            'D': [0.4, 0, 0, 0]
        })

class Process(object):
    def __init__(self, env, time, cost, revenue, name) -> None:
        self.env = env
        self.time = time
        self.cost = cost
        self.revenue = revenue
        self.W = 1
        self.WN = False
        self.name = name
    
    def lifecycle(self, entity, total_cost, total_revenue):
        print(f'Started working on process: {self.name}')
        yield self.env.timeout(self.time * self.W)
        print(f'Time after step in lifecycle: {self.env.now}')
        self.W = 0
      #  entity.action.interrupt() #Interrupts might work, but currently do not. 
        


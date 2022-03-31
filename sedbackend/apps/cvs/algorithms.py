import simpy
import random


class Process:
    def __init__(self, env, time, cost, revenue, name):
        self.env = env
        self.revenue = revenue
        self.cost = cost
        self.time = time
        self.name = name

    def run(self):
        print(f"{self.name} started at {self.env.now}")
        yield self.env.timeout(self.time)
        print(f"{self.name} finished at {self.env.now}")


class Simulation:
    def __init__(self):
        self.env = simpy.Environment()

    def run(self):
        self.env.process(process_generator(self.env))
        self.env.run()


def process_generator(env):
    i = 0
    while i < 2:
        t = random.randrange(1, 10)
        c = random.randrange(1, 10)
        r = random.randrange(1, 10)
        p = Process(env, t, c, r, name=f"Process {i}")
        env.process(p.run())
        yield env.timeout(t)
        i += 1


simulation = Simulation()
simulation.run()
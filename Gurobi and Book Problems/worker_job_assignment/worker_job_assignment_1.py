import pyomo.environ as pyo
from pyomo.opt import SolverFactory

worker_time_data = [
    [10, 15, 10, 15, 0], 
    [12, 8, 20, 16, 0], 
    [12, 9, 12, 18, 0], 
    [6, 12, 15, 18, 0], 
    [16, 12, 8, 12, 0]
    ]

# Model

model = pyo.ConcreteModel()

# Sets

model.workers = pyo.RangeSet(1, 5)
model.jobs = pyo.RangeSet(1, 5)

# Variables

model.x = pyo.Var(model.workers, model.jobs, 
                  within = pyo.Binary)
x = model.x

# Constraints

def one_worker_one_job(model, w):
    return pyo.quicksum(x[w, j] 
                        for j in model.jobs) == 1
model.c1 = pyo.Constraint(model.workers, rule = one_worker_one_job)

def one_job_one_worker(model, j):
    return pyo.quicksum(x[w, j] 
                        for w in model.workers) == 1
model.c2 = pyo.Constraint(model.jobs, rule = one_job_one_worker)

# Objective Function

def obj_fn(model):
    return pyo.quicksum(x[w, j]*worker_time_data[w-1][j-1] 
                        for w in model.workers 
                        for j in model.jobs)
model.obj = pyo.Objective(rule = obj_fn, sense = pyo.minimize)

# Solution

sol = SolverFactory("cplex")
res = sol.solve(model)

# Printing the Solution

for w in model.workers:
    for j in model.jobs:
        if x[w, j]() and x[w, j]() >= 0.9:
            print(f"Worker-{w} alloted Job-{j}")

print(f"Total time taken by all workers - {model.obj()} min.")
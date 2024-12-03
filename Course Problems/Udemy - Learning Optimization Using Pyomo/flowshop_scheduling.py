import pyomo.environ as pyo
from pyomo.opt import SolverFactory

N_JOBS = 6
N_MACHINES = 3

# Model

model= pyo.ConcreteModel()

# Sets

model.j = pyo.RangeSet(1, N_JOBS)
model.m = pyo.RangeSet(1, N_MACHINES)

model.j_1 = pyo.RangeSet(1, N_JOBS-1)
model.m_1 = pyo.RangeSet(1, N_MACHINES-1)

# Params

durations_list = [
    [3, 6, 3, 5, 5, 7], 
    [5, 4, 2, 4, 4, 5], 
    [5, 2, 4, 6, 3, 6]
    ]

model.durations = pyo.Param(model.m, model.j, 
                            within = pyo.Any, 
                            initialize = {
                                (i, j) : durations_list[i-1][j-1] 
                                for i in model.m
                                for j in model.j
                                })
durations = model.durations

# Variables

model.rank = pyo.Var(model.j, model.j, within = pyo.Binary)
rank = model.rank

model.empty = pyo.Var(model.m, model.j_1, 
                      within = pyo.NonNegativeReals)
empty = model.empty

model.idle = pyo.Var(model.m_1, model.j, 
                     within = pyo.NonNegativeReals)
idle = model.idle

model.start = pyo.Var(model.m, model.j, within = pyo.NonNegativeReals)
start = model.start

# Constraints

def rank_job(model, k):
    return sum(rank[j, k] for j in model.j) == 1
model.c1 = pyo.Constraint(model.j, rule = rank_job)

def job_rank(model, j):
    return sum(rank[j, k] for k in model.j) == 1
model.c2 = pyo.Constraint(model.j, rule = job_rank)

def between_machines(model, m_1, k_1):
    return (empty[m_1, k_1] + sum(durations[m_1, j]*rank[j, k_1 + 1] for j in model.j) + idle[m_1, k_1 + 1] 
            == idle[m_1, k_1] + sum(durations[m_1+1, j]*rank[j, k_1] for j in model.j) + empty[m_1 + 1, k_1])
model.c3 = pyo.Constraint(model.m_1, model.j_1, rule = between_machines)

def start_times(model, m, k):
    return (start[m, k] == sum(durations[u, j]*rank[j, 1] for u in model.m_1 for j in model.j) 
            + sum(durations[m, j]*rank[j, r] for j in model.j for r in model.j_1) 
            + sum(empty[m, r] for r in model.j_1))
model.c4 = pyo.Constraint(model.m, model.j, rule = start_times)

def no_idle_for_m1(model, k_1):
    return empty[1, k_1] == 0
model.c5 = pyo.Constraint(model.j_1, rule = no_idle_for_m1)

def no_wait_for_j1(model, m_1):
    return idle[m_1, 1] == 0
model.c6 = pyo.Constraint(model.m_1, rule = no_wait_for_j1)

# Objective Function

def obj_fn(model):
    return (sum(durations[m_1, j]*rank[j, 1] for m_1 in model.m_1 for j in model.j) 
            + sum(empty[N_MACHINES, k_1] for k_1 in model.j_1))
model.obj = pyo.Objective(rule = obj_fn, sense = pyo.minimize)

# def obj_fn(model):
#     return start[N_MACHINES, N_JOBS]
# model.obj = pyo.Objective(rule = obj_fn, sense = pyo.minimize)

# Solution

sol = SolverFactory("cplex")
res = sol.solve(model)

print(res)

for j in model.j:
    for k in model.j:
        if rank[j, k]():
            print(f"Rank-{k} = {j}")
        

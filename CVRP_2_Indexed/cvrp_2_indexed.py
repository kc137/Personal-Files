import pyomo.environ as pyo, matplotlib.pyplot as plt, networkx as nx
from pyomo.opt import SolverFactory
from cvrp_2_indexed_data import matrix, NV, coords, demands, capacity as Q

model = pyo.ConcreteModel()

NC = len(matrix)

# Sets and Parameters

model.N = pyo.RangeSet(1, NC)
model.C = pyo.RangeSet(2, NC)

# Variables

model.x = pyo.Var(model.N, model.N, within = pyo.Binary)
x = model.x

model.q = pyo.Var(model.N, within = pyo.NonNegativeReals, bounds = (0, Q))
q = model.q

# Constraints

def once(model, j):
    return pyo.quicksum(x[i, j] for i in model.N if i != j) == 1
model.c1 = pyo.Constraint(model.C, rule = once)

def flow(model, j):
    return pyo.quicksum(x[i, j] for i in model.N if i != j) == \
           pyo.quicksum(x[j, i] for i in model.N if i != j)
model.c2 = pyo.Constraint(model.C, rule = flow)

def demand(model, i, j):
    if i != j:
        return q[i] + demands[j-1] <= q[j] + Q*(1 - x[i, j])
    else:
        return pyo.Constraint.Skip
model.c3 = pyo.Constraint(model.N, model.C, rule = demand)

# def depot(model):
#     return pyo.quicksum(x[1, j] for j in model.C) == 1
# model.c4 = pyo.Constraint(rule = depot)

def total_trips1(model):
    return pyo.quicksum(x[1, j] for j in model.C) >= 1
model.c5 = pyo.Constraint(rule = total_trips1)

def total_trips2(model):
    return pyo.quicksum(x[1, j] for j in model.C) <= NV
model.c6 = pyo.Constraint(rule = total_trips2)

def to_and_fro(model):
    return pyo.quicksum(x[1, j] for j in model.C) == \
           pyo.quicksum(x[j, 1] for j in model.C)
model.c7 = pyo.Constraint(rule = to_and_fro)

# Objective Function

def obj_fn(model):
    return pyo.quicksum(x[i, j]*matrix[i-1][j-1] 
                        for i in model.N 
                        for j in model.N if i != j)
model.obj = pyo.Objective(rule = obj_fn, sense = pyo.minimize)

# Solution

sol = SolverFactory("cplex", solver_io = "python")
sol.options["timelimit"] = 15
res = sol.solve(model)

# Printing the Solution

print(f"Total distance for the CVRP Problem by all Vehicles : {model.obj()} km.")

arcs = []

for i in model.N:
    for j in model.N:
        if x[i, j]() and x[i, j]() >= 0.9:
            arcs.append((i, j))
            
origins = []

for j in model.C:
    if x[1, j]() and x[1, j]() >= 0.9:
        origins.append((1, j))

arcs = []

routes = {v + 1 : [origins[v]] for v in range(len(origins))}

for i in model.N:
    for j in model.N:
        if i != j and x[i, j]() and x[i, j]() >= 0.9:
            arcs.append((i, j))

path_creation = 0

routes = {v + 1 : [origins[v]] for v in range(len(origins))}

while path_creation < len(origins):
    for i, j in arcs:
        for v in routes:
            if routes[v][-1][-1] == i and routes[v][-1][-1] != 1:
                routes[v].append((i, j))
        for v in routes:
            if routes[v][-1][-1] == 1:
                path_creation += 1
        if path_creation < len(origins):
            path_creation = 0

vehicle_nodes = {v : [] for v in routes}


for v in vehicle_nodes:
    for i, j in routes[v]:
        if j != model.N.at(1):
            vehicle_nodes[v].append(j)
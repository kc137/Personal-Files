import pyomo.environ as pyo
from pyomo.opt import SolverFactory
from air_hub_data import FACTOR, NAMES, DIST, QUANT, N_HUBS

# Model

model = pyo.ConcreteModel()

# Sets and Params

model.cities = pyo.RangeSet(1, 6)
cities = model.cities

# Variables

model.flow = pyo.Var(cities, cities, cities, cities, within = pyo.Binary)
flow = model.flow

model.hub = pyo.Var(cities, within = pyo.Binary)
hub = model.hub

# Constraints

def total_hubs(model):
    return pyo.quicksum(hub[c] for c in cities) == N_HUBS
model.c1 = pyo.Constraint(rule = total_hubs)

def assign_single_pair(model, i, j):
    if i != j:
        return pyo.quicksum(flow[i, j, k, l] 
                            for k in cities 
                            for l in cities) == 1
    else:
        return pyo.Constraint.Skip
model.c2 = pyo.Constraint(cities, cities, rule = assign_single_pair)

model.hub_cons = pyo.ConstraintList()

for i in cities:
    for j in cities:
        for k in cities:
            for l in cities:
                if i != j:
                    model.hub_cons.add(flow[i, j, k, l] <= hub[k])
                    model.hub_cons.add(flow[i, j, k, l] <= hub[l])

# Objective Function

def obj_fn(model):
    return pyo.quicksum(
        (DIST[i-1][k-1] + DIST[j-1][l-1] + FACTOR*DIST[k-1][l-1])
        *(QUANT[i-1][j-1])*(flow[i, j, k, l]) 
        for i in cities 
        for j in cities 
        for k in cities 
        for l in cities if i != j)
model.obj = pyo.Objective(rule = obj_fn, sense = pyo.minimize)

# Solution

sol = SolverFactory("cplex")
res = sol.solve(model)

# Printing the Solution

print(res)

for i in cities:
    for j in cities:
        for k in cities:
            for l in cities:
                if i != j:
                    if flow[i, j, k, l]() and flow[i, j, k, l]() >= 0.9:
                        # print(f"Freight transported from city-{NAMES[i-1]} to city-{NAMES[j-1]} "
                        #       f"through hubs {NAMES[k-1]} and {NAMES[l-1]}")
                        print(f"flow{[NAMES[i-1], NAMES[j-1], NAMES[k-1], NAMES[l-1]]} = {flow[i, j, k, l]()}")

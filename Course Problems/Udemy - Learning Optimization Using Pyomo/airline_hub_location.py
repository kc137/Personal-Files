import pyomo.environ as pyo
from pyomo.opt import SolverFactory

model = pyo.ConcreteModel()

# Sets

model.cities = pyo.RangeSet(1, 6)

# Params

cities_dict = {
    1 : "Atlanta", 
    2 : "Boston", 
    3 : "Chicago", 
    4 : "Marseille", 
    5 : "Nice", 
    6 : "Paris"
    }

model.hubs = pyo.Param(within = pyo.Any, initialize = 2)

quantities = [
    [0, 500, 1000, 300, 400, 1500], 
    [1500, 0, 250, 630, 360, 1140], 
    [400, 510, 0, 460, 320, 490], 
    [300, 600, 810, 0, 820, 310], 
    [400, 100, 420, 730, 0, 970], 
    [350, 1020, 260, 580, 380, 0]
    ]

dist_matrix = [
    [0, 945, 605, 4667, 4749, 4394], 
    [945, 0, 866, 3726, 3806, 3448], 
    [605, 866, 0, 4471, 4541, 4152], 
    [4667, 3726, 4471, 0, 109, 415], 
    [4749, 3806, 4541, 109, 0, 431], 
    [4394, 3448, 4152, 415, 431, 0]
    ]

# Variables

model.flow = pyo.Var(model.cities, model.cities, model.cities, model.cities, 
                     within = pyo.Binary)
flow = model.flow

model.hub = pyo.Var(model.cities, within = pyo.Binary)
hub = model.hub

# Constraints

def hub_cons(model):
    return sum(hub[i] for i in model.cities) == model.hubs
model.c1 = pyo.Constraint(rule = hub_cons)

def flow_cons(model, i, j):
    if i != j:
        return sum(flow[i, j, k, l] for k in model.cities for l in model.cities) == 1
    else:
        return hub[i] == hub[i]
model.c2 = pyo.Constraint(model.cities, model.cities, rule = flow_cons)

def hub_k_cons(model, i, j, k, l):
    if i != j:
        return flow[i, j, k, l] <= hub[k]
    else:
        return flow[i, j, k, l] == flow[i, j, k, l]
model.c3 = pyo.Constraint(model.cities, model.cities, model.cities, model.cities, 
                          rule = hub_k_cons)

def hub_l_cons(model, i, j, k, l):
    if i != j: #  and k != l
        return flow[i, j, k, l] <= hub[l]
    else:
        return flow[i, j, k, l] == flow[i, j, k, l]
model.c4 = pyo.Constraint(model.cities, model.cities, model.cities, model.cities, 
                          rule = hub_l_cons)

# Objective Function

def obj_fn(model):
    cost = sum((dist_matrix[i-1][k-1] + 0.8*dist_matrix[k-1][l-1] + dist_matrix[l-1][j-1])*quantities[i-1][j-1]*flow[i, j, k, l]
                for i in model.cities 
                for j in model.cities 
                for k in model.cities 
                for l in model.cities if i != j)
    return cost
model.obj = pyo.Objective(rule = obj_fn, sense = pyo.minimize)

# Solution

sol = SolverFactory("cplex")
res = sol.solve(model)

print(f"Total Cost : {model.obj()} $")

for i in model.cities:
    print(f"{hub[i]()}")

for i in model.cities:
    for j in model.cities:
        for k in model.cities:
            for l in model.cities:
                if flow[i, j, k, l]():
                    print(f"flow{[cities_dict[i], cities_dict[j], cities_dict[k], cities_dict[l]]} = {flow[i, j, k, l]()}")



















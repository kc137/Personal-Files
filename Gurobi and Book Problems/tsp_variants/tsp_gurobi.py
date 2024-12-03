import pyomo.environ as pyo, json, math, numpy as np
from pyomo.opt import SolverFactory

with open("capitals.json") as cap:
    data = json.load(cap)

state_names = [data[code]["name"] for code in data]
state_names = state_names
N = len(state_names)

coords = [(float(data[code]["lat"]), float(data[code]["long"])) 
          for code in data]

distance_network = {(state_names[i], state_names[j]) : 
                    (math.hypot(coords[i][0] - coords[j][0], 
                               coords[i][1] - coords[j][1])) 
                    for i in range(len(state_names)) 
                    for j in range(len(state_names)) 
                    if i != j
                    }

distance_matrix = np.zeros(shape = [len(state_names), len(state_names)], 
                           dtype = int)
for i in range(50):
    for j in range(50):
        if i != j:
            distance_matrix[i][j] = math.hypot(coords[i][0] - coords[j][0], 
                                               coords[i][1] - coords[j][1])

# Model

model = pyo.ConcreteModel()

# Variables

model.x = pyo.Var(distance_network.keys(), within = pyo.Binary)
x = model.x

model.u = pyo.Var(state_names, within = pyo.NonNegativeReals)
u = model.u

# Constraints

def row_once(model, i):
    return pyo.quicksum(x[i, j] 
                        for (i1, j) in distance_network 
                        if i != j and i == i1) == 1
model.c1 = pyo.Constraint(state_names, rule = row_once)

def col_once(model, j):
    return pyo.quicksum(x[i, j] 
                        for (i, j1) in distance_network 
                        if i != j and j == j1) == 1
model.c2 = pyo.Constraint(state_names, rule = col_once)

model.sub_tour = pyo.ConstraintList()

for i in state_names[1:]:
    for j in state_names[1:]:
        if i != j:
            model.sub_tour.add(
                u[i] - u[j] + N*(x[i, j]) <= N-1
                )

def sub_tour_cons(model, i, j):
    if i != j and (i != state_names[0] or j != state_names[0]):
        return x[i, j] == x[j, i]
    else:
        return pyo.Constraint.Skip
# model.c3 = pyo.Constraint(state_names, state_names, rule = sub_tour_cons)

# Objective Function

def obj_fn(model):
    return pyo.quicksum(x[i, j]*distance_network[i, j] 
                        for i, j in distance_network)
model.obj = pyo.Objective(rule = obj_fn, sense = pyo.minimize)

# # Solution

# sol = SolverFactory("cplex")
# sol.options["timelimit"] = 20
# res = sol.solve(model)

# # Printing the Solution

# print(res)
# tours = 0

# for i in state_names:
#     for j in state_names:
#         if i != j and x[i, j]() and x[i, j]() >= 0.9:
#             print(f"{x[i, j]} = {x[i, j]()}")
#             tours += 1














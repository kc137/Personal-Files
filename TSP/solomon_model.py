import pyomo.environ as pyo
from pyomo.opt import SolverFactory
from data_file import N, distance_matrix, time_windows

# Model

model = pyo.ConcreteModel()

# Sets and Params

model.N = pyo.RangeSet(1, N)
model.C = pyo.RangeSet(2, N)

# Variables

model.x = pyo.Var(model.N, model.N, within = pyo.Binary)
x = model.x

model.t = pyo.Var(model.N, within = pyo.NonNegativeReals)
t = model.t

# Constraints

def city_row_once(model, j):
    return pyo.quicksum(x[i, j] 
                        for i in model.N 
                        if i != j) == 1
model.c1 = pyo.Constraint(model.N, rule = city_row_once)

def city_col_once(model, i):
    return pyo.quicksum(x[i, j] 
                        for j in model.N 
                        if i != j) == 1
model.c2 = pyo.Constraint(model.N, rule = city_col_once)

model.time_bound_cons = pyo.ConstraintList()

for i in model.N:
    model.time_bound_cons.add(
        (time_windows[i-1][0], t[i], time_windows[i-1][1])
        )
    
model.time_flow_cons = pyo.ConstraintList()

for i in model.C:
    for j in model.C:
        if i != j:
            model.time_flow_cons.add(
                t[i] + x[i, j]*distance_matrix[i-1][j-1] <= t[j] + (1 - x[i, j])*2000
                )

# Objective Function

def obj_fn(model):
    return pyo.quicksum(x[i, j]*distance_matrix[i-1][j-1] 
                        for i in model.N 
                        for j in model.N 
                        if i != j)
model.obj = pyo.Objective(rule = obj_fn, sense = pyo.minimize)

# Solution

sol = SolverFactory("cplex")
res = sol.solve(model)

# Printing the Solution

print(res)

arcs = []

for i in model.N:
    for j in model.N:
        if i != j:
            if x[i, j]() and x[i, j]() >= 0.9:
                arcs.append((i, j))
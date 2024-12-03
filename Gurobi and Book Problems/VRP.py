import pyomo.environ as pyo, pandas as pd
from pyomo.opt import SolverFactory
from itertools import combinations

model = pyo.ConcreteModel()

# Sets and Parameters

M = 10000

model.v = pyo.Set(initialize = ["V1", "V2"])
V = model.v
model.c = pyo.Set(initialize = ["C1", "C2", "C3", "C4"])
C = model.c

model.demand = pyo.Param(C, initialize = {"C1" : 5, "C2" : 4, "C3" : 2, "C4" : 3})
model.capacity = pyo.Param(V, initialize = {"V1" : 10, "V2" : 8})
model.distance = pyo.Param(C, C, initialize = {('C1', 'C2'): 10, ('C1', 'C3'): 15, ('C1', 'C4'): 20,
                  ('C2', 'C1'): 10, ('C2', 'C3'): 5, ('C2', 'C4'): 15,
                  ('C3', 'C1'): 15, ('C3', 'C2'): 5, ('C3', 'C4'): 10,
                  ('C4', 'C1'): 20, ('C4', 'C2'): 15, ('C4', 'C3'): 10})
distance = model.distance

# Variables

model.x = pyo.Var(C, C, V, domain = pyo.Binary)
x = model.x

def demand(model, i):
    return sum(x[i, j, k] for j in C for k in V) == model.demand[i]
model.C1 = pyo.Constraint(C, rule = demand)

def capacity(model, k):
    return sum(x[i, j, k]*model.demand[j] for i in C for j in C if j != i) <= model.capacity[k]
model.C2 = pyo.Constraint(V, rule = capacity)

def flow(model, j):
    return sum(x[i, j, k] for i in C for k in V) == 1
model.C3 = pyo.Constraint(C, rule = flow)

def leave(model, j, k):
    return sum(x[i, j, k] for i in C if i != j) == sum(x[j, i, k] for i in C)
model.C4 = pyo.Constraint(C, V, rule = leave)

model.subtour = pyo.ConstraintList()
for r in range(2, len(C) + 1):
    for s in combinations(C, r):
        model.subtour.add(expr = sum(
            x[i, j, k] for i in s for j in s if j != i for k in V) <= len(s) - 1)

# Objective Function

def Obj_Fn(model):
    return sum(distance[i, j]*x[i, j, k] for i in C for j in C for k in V if i != j)
model.Obj = pyo.Objective(rule = Obj_Fn, sense = pyo.minimize)

# Solution

sol = SolverFactory("cplex")
res = sol.solve(model)

for i in C:
    for j in C:
        for k in V:
            print(f"{x[i, j, k]} = { x[i, j, k]()}")


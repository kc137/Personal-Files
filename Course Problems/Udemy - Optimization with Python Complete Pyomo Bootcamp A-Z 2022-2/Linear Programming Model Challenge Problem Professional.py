import pyomo.environ as pyo
from pyomo.opt import SolverFactory

model = pyo.ConcreteModel()

costs = [
    [8, 6, 10, 9], 
    [9, 12, 13, 7], 
    [14, 9, 16, 5]
    ]

supply = [35, 50, 40]
demands = [45, 20, 30, 30]

# Sets and Parameters

model.P = pyo.RangeSet(1, 3)
model.C = pyo.RangeSet(1, 4)

# Variables

model.x = pyo.Var(model.P, model.C, within = pyo.NonNegativeReals)
x = model.x

# Constraints

def supply_cons(model, p):
    return sum(x[p, c] for c in model.C) <= supply[p-1]
model.c1 = pyo.Constraint(model.P, rule = supply_cons)

def demand_cons(model, d):
    return sum(x[p, d] for p in model.P) >= demands[d-1]
model.c2 = pyo.Constraint(model.C, rule = demand_cons)

# Objective Function

def obj_fn(model):
    return sum(x[p, c]*costs[p-1][c-1] 
               for p in model.P 
               for c in model.C)
model.obj = pyo.Objective(rule = obj_fn, sense = pyo.minimize)

# Solution

sol = SolverFactory("cplex")
res = sol.solve(model)

# Printing the Solution

for p in model.P:
    for c in model.C:
        print(f"Electricity from Plant-{p} - City-{c} : {x[p, c]()} mill kwh.")

print(f"Total minimized cost : {model.obj()}")

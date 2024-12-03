import pyomo.environ as pyo
from pyomo.opt import SolverFactory
from heating_oil_delivery_data import DEM, DIST, CAP

# Model

model = pyo.ConcreteModel()

NC = len(DIST)

# Sets and Params

model.N = pyo.RangeSet(1, NC)
model.C = pyo.RangeSet(2, NC)

# Variables

model.x = pyo.Var(model.N, model.N, within = pyo.Binary)
x = model.x

model.q = pyo.Var(model.N, within = pyo.NonNegativeReals)
q = model.q

# Constraints

def once(model, j):
    return pyo.quicksum(x[i, j] 
                        for i in model.N 
                        if i != j) == 1
model.c1 = pyo.Constraint(model.C, rule = once)

def flow(model, j):
    return (pyo.quicksum(x[i, j] for i in model.N if i != j) == 
            pyo.quicksum(x[j, i] for i in model.N if i != j))
model.c2 = pyo.Constraint(model.C, rule = flow)

def demand_cons(model, i, j):
    if i != j:
        return q[i] + DEM[j-1] <= q[j] + CAP*(1 - x[i, j])
    else:
        return pyo.Constraint.Skip
model.c3 = pyo.Constraint(model.N, model.C, rule = demand_cons)

def total_trips(model):
    return (1, pyo.quicksum(x[1, j] for j in model.C), 2)
model.c4 = pyo.Constraint(rule = total_trips)

# Objective Function

def obj_fn(model):
    return pyo.quicksum(x[i, j]*DIST[i-1][j-1] 
                        for i in model.N 
                        for j in model.N 
                        if i != j)
model.obj = pyo.Objective(rule = obj_fn, sense = pyo.minimize)

# Solution

sol = SolverFactory("cplex")
res = sol.solve(model)

# Printing the Solution

print(res)
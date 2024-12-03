import pyomo.environ as pyo
from pyomo.opt import SolverFactory
from c2glass import *

"""
CPROD, CSTOCK, FSTOCK, ISTOCK, DEM, CAPW, CAPM, CAPS, TIMEW, TIMEM , SPACE
"""

# Model

model = pyo.ConcreteModel()

# Sets and Params

model.prods = pyo.RangeSet(1, 6)
model.weeks = pyo.RangeSet(1, 12)

# Variables

model.produce = pyo.Var(model.prods, model.weeks, 
                        within = pyo.NonNegativeReals)
produce = model.produce

model.store = pyo.Var(model.prods, model.weeks, 
                      within = pyo.NonNegativeReals)
store = model.store

# Constraints

def storage_equality(model, p, w):
    return (store[p, w] == 
            (ISTOCK[p-1] if w == 1 else store[p, w-1]) 
            + produce[p, w] 
            - DEM[p-1][w-1])
model.c1 = pyo.Constraint(model.prods, model.weeks, rule = storage_equality)

def final_stock_cons(model, p):
    return store[p, model.weeks.at(-1)] >= FSTOCK[p-1]
model.c2 = pyo.Constraint(model.prods, rule = final_stock_cons)

def worker_cons(model, w):
    return pyo.quicksum(TIMEW[p-1]*produce[p, w] 
                        for p in model.prods) <= CAPW
model.c3 = pyo.Constraint(model.weeks, rule = worker_cons)

def machine_cons(model, w):
    return pyo.quicksum(TIMEM[p-1]*produce[p, w] 
                        for p in model.prods) <= CAPM
model.c4 = pyo.Constraint(model.weeks, rule = machine_cons)

def space_cons(model, w):
    return pyo.quicksum(SPACE[p-1]*store[p, w] 
                        for p in model.prods) <= CAPS
model.c5 = pyo.Constraint(model.weeks, rule = space_cons)

# Objective Function

def obj_fn(model):
    return (pyo.quicksum(CPROD[p-1]*produce[p, w] 
                         for p in model.prods 
                         for w in model.weeks) 
            + pyo.quicksum(CSTOCK[p-1]*store[p, w] 
                                 for p in model.prods 
                                 for w in model.weeks))
model.obj = pyo.Objective(rule = obj_fn, sense = pyo.minimize)

# Solution

sol = SolverFactory("cplex")
res = sol.solve(model)

# Printing the Solution

print(res)

import pyomo.environ as pyo, pandas as pd, numpy as np
from mrp_1_data import REQ, CBUY, CPROD, CAP, DEM
from pyomo.opt import SolverFactory

# Model

model  = pyo.ConcreteModel()

# Variables

model.buy = pyo.Var(CBUY, within = pyo.NonNegativeIntegers)
buy = model.buy

model.produce = pyo.Var(CPROD, within = pyo.NonNegativeIntegers)
produce = model.produce

# Constraints

def demand_cons(model, p):
    return produce[p] >= DEM[p]
model.c1 = pyo.Constraint(DEM, rule = demand_cons)

def sufficient_production_with_assembly(model, p):
    try:
        if p in CPROD:
            return (buy[p] + produce[p] >= pyo.quicksum(REQ[q, p]*produce[q] 
                                                        for q in CPROD 
                                                        if (q, p) in REQ))
        else:
            return (buy[p] >= pyo.quicksum(REQ[q, p]*produce[q] 
                                           for q in CPROD 
                                           if (q, p) in REQ))
    except KeyError:
        return pyo.Constraint.Skip
model.c2 = pyo.Constraint(CBUY, rule = sufficient_production_with_assembly)

def capacity_cons(model, p):
    return produce[p] <= CAP[p]
model.c3 = pyo.Constraint(CPROD, rule = capacity_cons)

# Objective Function

def obj_fn(model):
    return (pyo.quicksum(CBUY[p]*buy[p] 
                         for p in CBUY) 
            + pyo.quicksum(CPROD[p]*produce[p] 
                                 for p in CPROD))
model.obj = pyo.Objective(rule = obj_fn, sense = pyo.minimize)

# Solution

sol = SolverFactory("cplex")
res = sol.solve(model)

# Printing the Solution

print(res)

for pre in CBUY:
    if pre not in CPROD:
        print(f"Quantity of {pre} bought : {buy[pre]()}")
    else:
        print(f"Quantity of {pre} sub-contracted : {buy[pre]()}")

for prod in CPROD:
    print(f"Quantity of {prod} assembled : {produce[prod]()}")
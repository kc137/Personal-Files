import pyomo.environ as pyo
from pyomo.opt import SolverFactory

# Model

model = pyo.ConcreteModel()

# Data

demands = [16500, 22000, 62000, 7500, 62000]
sales_price = [3.99, 3.86, 4.10, 4.24, 3.70]
cost_price = [2.66, 2.55, 2.49, 2.51, 2.50]
purchase_price = [2.86, 2.70, 2.60, 2.70, 2.70]

loom_speed_j = [4.63, 4.63, 5.23, 5.23, 4.17]
loom_speed_r = [0, 0, 5.23, 5.23, 4.17]

hours = 720

# Sets

model.fabrics = pyo.RangeSet(1, 5)
fabrics = model.fabrics

# Jacquard, Retier, Purchased
model.looms = pyo.Set(initialize = ["J", "R", "P"])
looms = model.looms

# Variables

model.x = pyo.Var(fabrics, looms, within = pyo.NonNegativeIntegers)
x = model.x

# Constraints

def time_cons_j(model):
    return (pyo.quicksum((x[f, "J"] / loom_speed_j[f-1]) 
                          for f in fabrics)) <= 720*8
model.c1 = pyo.Constraint(rule = time_cons_j)

def time_cons_r(model):
    return (pyo.quicksum((x[f, "R"] / loom_speed_r[f-1]) 
                   for f in fabrics 
                   if f >= 3)) <= 720*30
model.c2 = pyo.Constraint(rule = time_cons_r)

def demand_cons(model, f):
    if f >= 3:
        return pyo.quicksum(x[f, l] for l in looms) == demands[f-1]
    else:
        return pyo.quicksum(x[f, l] for l in looms 
                            if l != "R") == demands[f-1]
model.c3 = pyo.Constraint(fabrics, rule = demand_cons)

# Objective Function

def obj_fn(model):
    return (pyo.quicksum(x[f, l]*(sales_price[f-1] - cost_price[f-1]) 
                        for f in fabrics 
                        for l in looms 
                        if f <= 2 and l != "R" and l != "P") 
            + pyo.quicksum(x[f, l]*(sales_price[f-1] - cost_price[f-1]) 
                                for f in fabrics 
                                for l in looms 
                                if f >= 3 and l != "P") 
            + pyo.quicksum(x[f, "P"]*(sales_price[f-1] - purchase_price[f-1]) 
                                for f in fabrics))
model.obj = pyo.Objective(rule = obj_fn, sense = pyo.maximize)

# Solution

sol = SolverFactory("cplex", solver_io="python")
# sol = SolverFactory("glpk", executable = "C:\\Python\\glpk-4.65\\w64", 
#                     validate=False) # executable = "C:\\Python\\glpk-4.65\\w64"
res = sol.solve(model)

# Printing the Solution

print(res)
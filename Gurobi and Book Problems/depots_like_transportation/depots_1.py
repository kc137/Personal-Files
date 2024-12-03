import pyomo.environ as pyo
from pyomo.opt import SolverFactory
from depots_data import COST, CAP, CFIX, DEM

# Model

model = pyo.ConcreteModel()

# Sets

model.depots = pyo.RangeSet(1, len(CAP))
depots = model.depots

model.customers = pyo.RangeSet(1, len(DEM))
customers = model.customers

# Variables

model.x = pyo.Var(depots, customers, within = pyo.NonNegativeReals, 
                  bounds = (0, 1))
x = model.x

model.build = pyo.Var(depots, within = pyo.Binary)
build = model.build

# Constraints

def customer_once(model, c):
    return pyo.quicksum(x[d, c] for d in depots) == 1
model.c1 = pyo.Constraint(customers, rule = customer_once)

def capacity_cons(model, d):
    return pyo.quicksum(x[d, c]*DEM[c-1] for c in customers) <= CAP[d-1]*build[d]
model.c2 = pyo.Constraint(depots, rule = capacity_cons)

# Objective Function

def obj_fn(model):
    return (pyo.quicksum(CFIX[d-1]*build[d] 
                         for d in depots) 
            + pyo.quicksum(COST[d-1][c-1]*x[d, c] 
                           for d in depots 
                           for c in customers))
model.obj = pyo.Objective(rule = obj_fn, sense = pyo.minimize)

# Solution

sol = SolverFactory("cplex")
res = sol.solve(model)

# Printing the Solution

print(res)

for d in depots:
    if build[d]() and build[d]() >= 0.9:
        print(f"Depot-{d} built")
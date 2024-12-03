import pyomo.environ as pyo
from pyomo.opt import SolverFactory

# Model

model = pyo.ConcreteModel()

# Data

hours_req = [
    [3, 2, 1], 
    [4, 1, 3], 
    [2, 2, 2]
    ]

profits = [30, 40, 35]

max_hours = [90, 54, 93]

# Sets

model.products = pyo.RangeSet(1, 3)
products = model.products

model.machines = pyo.RangeSet(1, 3)
machines = model.machines

# Variables

model.x = pyo.Var(products, within = pyo.NonNegativeReals)
x = model.x

# Constraints

def max_hours_cons(model, m):
    return pyo.quicksum(x[p]*hours_req[p-1][m-1] 
                        for p in products) <= max_hours[m-1]
model.c1 = pyo.Constraint(machines, rule = max_hours_cons)

# Objective Function

def obj_fn(model):
    return pyo.quicksum(x[p]*profits[p-1] 
                        for p in products)
model.obj = pyo.Objective(rule = obj_fn, sense = pyo.maximize)

# Solution

sol = SolverFactory("cplex", solver_io = "python")
res = sol.solve(model)

# Printing the Solution

print(res)

for p in products:
    print(f"Total production of Product-{p} : {x[p]()}")
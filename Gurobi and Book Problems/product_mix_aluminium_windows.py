import pyomo.environ as pyo
from pyomo.opt import SolverFactory

# Model

model = pyo.ConcreteModel()

# Data

hours_req = [
    [1, 3, 2], 
    [2, 0, 3], 
    [1, 4, 0]
    ]

hours_avl = [400, 600, 600]

profits = [30, 20, 40]

# Sets

model.products = pyo.RangeSet(1, 3)
products = model.products

# Variables

model.x = pyo.Var(products, within = pyo.NonNegativeReals)
x = model.x

# Constraints

def hours_cons(model, i):
    return pyo.quicksum(x[p]*hours_req[i][p-1] 
                        for p in products) <= hours_avl[i]
model.c1 = pyo.Constraint(range(3), rule = hours_cons)

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
    print(f"Product-{p} produced : {x[p]()}")
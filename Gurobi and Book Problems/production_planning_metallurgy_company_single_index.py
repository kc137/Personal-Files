import pyomo.environ as pyo
from pyomo.opt import SolverFactory

# Model

model = pyo.ConcreteModel()

# Data

costs = [10, 5]

times = [
    [2, 3, 4, 2], 
    [3, 2, 1, 2]
    ]

prod_cap = [500, 380]

sales_price = [65, 70, 55, 45]

# Sets

model.machines = pyo.RangeSet(1, 2)
machines = model.machines

model.products = pyo.RangeSet(1, 4)
products = model.products

# Variables

model.x = pyo.Var(products, within = pyo.NonNegativeReals)
x = model.x

# Constraints

def prod_time(model, m):
    return pyo.quicksum(x[p]*times[m-1][p-1] for p in products) <= prod_cap[m-1]
model.c1 = pyo.Constraint(machines, rule = prod_time)

# Objective Function

def obj_fn(model):
    return (pyo.quicksum(x[p]*sales_price[p-1] 
                        for p in products) 
            - pyo.quicksum(x[p]*times[m-1][p-1]*costs[m-1] 
                           for m in machines 
                           for p in products))
model.obj = pyo.Objective(rule = obj_fn, sense = pyo.maximize)

# Solution

sol = SolverFactory("cplex", solver_io = "python")
res = sol.solve(model)

# Printing the Solution

print(res)

# for m in machines:
for p in products:
    print(f"No. of P-{p} : {x[p]()}")
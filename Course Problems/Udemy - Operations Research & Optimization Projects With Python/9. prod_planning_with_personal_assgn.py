import pyomo.environ as pyo
from pyomo.opt import SolverFactory

durations = [[1.3, 0.9, 2.0, 0.3, 0.9], 
             [1.8, 1.7, 1.4, 0.6, 1.1], 
             [1.3, 1.2, 1.3, 1.0, 1.4], 
             [0.9, 1.1, 1.0, 0.9, 1.0]]

transfers = [[0, 1, 1, 1, 0], 
             [0, 0, 1, 0, 1], 
             [1, 1, 0, 1, 0], 
             [0, 0, 0, 0, 1], 
             [1, 1, 1, 0, 0]]

profits = [7, 8, 9, 7]

capacities = [4500, 5000, 4500, 1500, 2500]

max_transfers = [400, 800, 200, 500, 300]

# Model

model = pyo.ConcreteModel()

# Sets

model.products = pyo.RangeSet(1, 4)
products = model.products

model.lines = pyo.RangeSet(1, 5)
lines = model.lines

# Variables

# For number of product to make

model.x = pyo.Var(products, within = pyo.NonNegativeIntegers)
x = model.x

# For transfers
model.t = pyo.Var(lines, lines, within = pyo.NonNegativeReals)
t = model.t

# For hours
model.h = pyo.Var(lines, within = pyo.NonNegativeReals)
h = model.h

# Constraints

def max_hours_cons(model, l):
    return pyo.quicksum(durations[p-1][l-1]*x[p] 
                        for p in products) <= h[l]
model.c1 = pyo.Constraint(lines, rule = max_hours_cons)

def transfer_balance(model, l):
    return (h[l] == capacities[l-1] + pyo.quicksum(t[k, l] for k in lines if transfers[k-1][l-1]) 
                                    - pyo.quicksum(t[l, k] for k in lines if transfers[l-1][k-1]))
model.c2 = pyo.Constraint(lines, rule = transfer_balance)

def max_transfer_cons(model, l):
    return pyo.quicksum(t[l, k] 
                        for k in lines 
                        if transfers[l-1][k-1]) <= max_transfers[l-1]
model.c3 = pyo.Constraint(lines, rule = max_transfer_cons)

# Objective Function

def obj_fn(model):
    return pyo.quicksum(x[p]*profits[p-1] 
                        for p in products)
model.obj = pyo.Objective(rule = obj_fn, sense = pyo.maximize)

# Solution

sol = SolverFactory("cplex")
res = sol.solve(model)

# Printing the Solution

print(res)

for p in products:
    print(f"The amount of product-{p} produced : {x[p]()}")







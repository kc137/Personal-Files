import pyomo.environ as pyo
from pyomo.opt import SolverFactory

max_capacity = 500
fixed_cost = 1000

model = pyo.ConcreteModel()

# Sets

model.i = pyo.RangeSet(1, 5)
model.j = pyo.RangeSet(1, 3)

cost_matrix = [
    [0 for _ in range(5)], 
    [0, 4, 5, 6, 8, 10], 
    [0, 6, 4, 3, 5, 8], 
    [0, 9, 7, 4, 3, 4], 
    ]

demands = [0, 80, 270, 250, 160, 180]

# Params

model.cost_network = pyo.Param(model.i, 
                               model.j, 
                               within = pyo.Any, 
                               initialize = {(i, j) : cost_matrix[j][i] 
                                             for i in model.i
                                             for j in model.j})
cost_network = model.cost_network

model.cust_demands = pyo.Param(model.i, 
                         within = pyo.NonNegativeReals, 
                         initialize = {
                             i : demands[i] for i in model.i
                             })
cust_demands = model.cust_demands

# Variables

model.x = pyo.Var(model.i, model.j, within = pyo.NonNegativeIntegers)
x = model.x

model.y = pyo.Var(model.i, within = pyo.Binary)
y = model.y

# Constraints

def demand_cons(model, i):
    return sum(x[i, j] for j in model.j) == cust_demands[i]
model.c1 = pyo.Constraint(model.i, rule = demand_cons)

def capacity_cons(model, j):
    return sum(x[i, j] for i in model.i) <= max_capacity*y[j]
model.c2 = pyo.Constraint(model.j, rule = capacity_cons)

def upper_bound_cons(model, i, j):
    return x[i, j] <= cust_demands[i]*y[j]
model.c3 = pyo.Constraint(model.i, model.j, rule = upper_bound_cons)

# Objective Function

def obj_fn(model):
    return (fixed_cost*sum(y[j] for j in model.j) + 
            sum(cost_network[(i, j)]*x[i, j] 
                for i in model.i 
                for j in model.j))
model.obj = pyo.Objective(rule = obj_fn)

# Solution

sol = SolverFactory("cplex")
res = sol.solve(model)

for j in model.j:
    for i in model.i:
        if x[i, j]():
            print(f"Warehouse-{j} ---> Customer-{i} :- {x[i, j]()} Units.")
        else:
            print(f"Warehouse-{j} ---> Customer-{i} :- 0 Units.")

print(f"Total Cost : {model.obj()} $")







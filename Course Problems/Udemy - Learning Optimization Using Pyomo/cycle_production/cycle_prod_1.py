import pyomo.environ as pyo
from pyomo.opt import SolverFactory

forecasts = [30, 15, 15, 25, 33, 40, 45, 45, 26, 14, 25, 30]

initial_stock = 2
prod_cost = 32
prod_over_cost = 40
storage_cost = 5
capacity = 30

# Model

model = pyo.ConcreteModel()

# Sets and Params

model.months = pyo.RangeSet(1, 12)
months = model.months

# Variables

model.prod = pyo.Var(months, within = pyo.NonNegativeReals)
prod = model.prod

model.prod_over = pyo.Var(months, within = pyo.NonNegativeReals)
prod_over = model.prod_over

model.storage = pyo.Var(months, within = pyo.NonNegativeReals)
storage = model.storage

# Constraints

def storage_cons(model, m):
    if m == 1:
        return prod[m] + prod_over[m] + initial_stock == storage[m] + forecasts[m-1]
    else:
        return prod[m] + prod_over[m] + storage[m-1] == storage[m] + forecasts[m-1]
model.c1 = pyo.Constraint(months, rule = storage_cons)

def prod_capacity(model, m):
    return prod[m] <= capacity
model.c2 = pyo.Constraint(months, rule = prod_capacity)

def prod_over_capacity(model, m):
    return prod_over[m] <= 0.5*capacity
model.c3 = pyo.Constraint(months, rule = prod_over_capacity)

# Objective Function

def obj_fn(model):
    return (pyo.quicksum(prod_cost*prod[m] 
                        for m in months) 
            + pyo.quicksum(prod_over_cost*prod_over[m] 
                                for m in months) 
            + pyo.quicksum(storage_cost*storage[m] 
                                for m in months))
model.obj = pyo.Objective(rule = obj_fn, sense = pyo.minimize)

# Solution

sol = SolverFactory("cplex")
res = sol.solve(model)

# Printing the Solution

print(res)




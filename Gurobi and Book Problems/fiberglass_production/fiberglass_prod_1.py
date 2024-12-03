import pyomo.environ as pyo
from pyomo.opt import SolverFactory

# Model

model = pyo.ConcreteModel()

# Parameters

prod_capacity = [140, 100, 110, 100, 120, 100]
demands = [100, 120, 100, 90, 120, 110]
prod_cost = [5, 8, 6, 6, 7, 6]
storage_cost = [0.2, 0.3, 0.2, 0.25, 0.3, 0.4]

# Sets

model.weeks = pyo.RangeSet(1, 6)
weeks = model.weeks

# Variables

model.prod_quantity = pyo.Var(weeks, within = pyo.NonNegativeReals)
prod_quantity = model.prod_quantity

model.storage = pyo.Var(weeks, within = pyo.NonNegativeReals)
storage = model.storage

# Constraints

def prod_capacity_cons(model, w):
    return prod_quantity[w] <= prod_capacity[w-1]
model.c1 = pyo.Constraint(weeks, rule = prod_capacity_cons)

def storage_cons(model, w):
    if w > 1:
        return storage[w] == storage[w-1] + prod_quantity[w] - demands[w-1]
    else:
        return storage[w] == prod_quantity[w] - demands[w-1]
model.c2 = pyo.Constraint(weeks, rule = storage_cons)

# Objective Function

def obj_fn(model):
    return (pyo.quicksum(prod_quantity[w]*prod_cost[w-1] 
                        for w in weeks) 
            + pyo.quicksum(storage[w]*storage_cost[w-1] 
                                for w in weeks))
model.obj = pyo.Objective(rule = obj_fn, sense = pyo.minimize)

# Solution

sol = SolverFactory("cplex")
res = sol.solve(model)

# Printing the Solution

print(res)

for w in weeks:
    print(f"Production for Week-{w} : {prod_quantity[w]()}")
    print(f"Storage for Week-{w} : {storage[w]()}")
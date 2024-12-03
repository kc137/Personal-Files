import pyomo.environ as pyo
from c4compo import CPROD, CRED, CADD, CSTOCK, DEM, ISTOCK, FSTOCK, PNAME
from pyomo.opt import SolverFactory

# Model

model = pyo.ConcreteModel()

# Sets and Params

model.months = pyo.RangeSet(1, 6)
months = model.months

model.products = pyo.RangeSet(1, 4)
products = model.products

# Variables

model.produce = pyo.Var(products, months, within = pyo.NonNegativeReals)
produce = model.produce

model.store = pyo.Var(products, months, within = pyo.NonNegativeReals)
store = model.store

model.add = pyo.Var(months, within = pyo.NonNegativeReals)
add = model.add

model.reduce = pyo.Var(months, within = pyo.NonNegativeReals)
reduce = model.reduce

# Constraints

def storage_equality(model, p, t):
    return (store[p, t] 
            == (store[p, t-1] 
                if t > 1 else ISTOCK[t-1]) 
            + produce[p, t] 
            - DEM[p-1][t-1])
model.c1 = pyo.Constraint(products, months, rule = storage_equality)

def final_storage_cons(model, p):
    return store[p, months.at(-1)] == FSTOCK[p-1]
model.c2 = pyo.Constraint(products, rule = final_storage_cons)

def produce_cons(model, t):
    if t > 1:
        return (pyo.quicksum(produce[p, t] 
                            for p in products) 
                - pyo.quicksum(produce[p, t-1] 
                                    for p in products) 
                == add[t] - reduce[t])
    else:
        return pyo.Constraint.Skip
model.c3 = pyo.Constraint(months, rule = produce_cons)

# Objective Function

def obj_fn(model):
    return (pyo.quicksum(CPROD[p-1]*produce[p, t] 
                         for p in products 
                         for t in months) 
            + pyo.quicksum(CSTOCK[p-1]*store[p, t] 
                                 for p in products 
                                 for t in months) 
            + pyo.quicksum(CADD*add[t] 
                                 for t in months 
                                 if t > 1)
            + pyo.quicksum(CRED*reduce[t] 
                                 for t in months 
                                 if t > 1))
model.obj = pyo.Objective(rule = obj_fn, sense = pyo.minimize)

# Solution

sol = SolverFactory("cplex")
res = sol.solve(model)

# Printing the Solution

print(res)

product_sum = []

for t in months:
    curr_sum = 0
    for p in products:
        print(f"produce[{p}, {t}] = {produce[p, t]()}")
        curr_sum += produce[p, t]()
    product_sum.append(curr_sum)
        
for p in products:
    for t in months:
        print(f"store[{p}, {t}] = {store[p, t]()}")

print(product_sum)
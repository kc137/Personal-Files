import pyomo.environ as pyo, pandas as pd
from pyomo.opt import SolverFactory

months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun"]

oils = ["VEG1", "VEG2", "OIL1", "OIL2", "OIL3"]

cost = {
    ('Jan', 'VEG1'): 110,
    ('Jan', 'VEG2'): 120,
    ('Jan', 'OIL1'): 130,
    ('Jan', 'OIL2'): 110,
    ('Jan', 'OIL3'): 115,
    ('Feb', 'VEG1'): 130,
    ('Feb', 'VEG2'): 130,
    ('Feb', 'OIL1'): 110,
    ('Feb', 'OIL2'): 90,
    ('Feb', 'OIL3'): 115,
    ('Mar', 'VEG1'): 110,
    ('Mar', 'VEG2'): 140,
    ('Mar', 'OIL1'): 130,
    ('Mar', 'OIL2'): 100,
    ('Mar', 'OIL3'): 95,
    ('Apr', 'VEG1'): 120,
    ('Apr', 'VEG2'): 110,
    ('Apr', 'OIL1'): 120,
    ('Apr', 'OIL2'): 120,
    ('Apr', 'OIL3'): 125,
    ('May', 'VEG1'): 100,
    ('May', 'VEG2'): 120,
    ('May', 'OIL1'): 150,
    ('May', 'OIL2'): 110,
    ('May', 'OIL3'): 105,
    ('Jun', 'VEG1'): 90,
    ('Jun', 'VEG2'): 100,
    ('Jun', 'OIL1'): 140,
    ('Jun', 'OIL2'): 80,
    ('Jun', 'OIL3'): 135
}

hardness = {"VEG1": 8.8, "VEG2": 6.1, "OIL1": 2.0, "OIL2": 4.2, "OIL3": 5.0}

price = 150 # Selling Price
init_store = 500 # Initial Storage
target_store = 500 # Last month storage
veg_cap = 200 # Max. prod. of vegetable oil
non_veg_cap = 250 # Max. prod. of non-vegetable oil

min_hardness = 3
max_hardness = 6
inv_cost = 5

# Model

model = pyo.ConcreteModel()

# Variables

# Quantity of food produced in each month
model.produce = pyo.Var(months, within = pyo.NonNegativeReals)
produce = model.produce

# Quantity of product (oil) bought in each month
model.buy = pyo.Var(months, oils, within = pyo.NonNegativeReals)
buy = model.buy

# Quantity of product (oil) consumed in each month
model.consume = pyo.Var(months, oils, within = pyo.NonNegativeReals)
consume = model.consume

# Quantity of product(oil) stored each month
model.store = pyo.Var(months, oils, within = pyo.NonNegativeReals)
store = model.store

# Constraints

# Balance for month Jan
def balance(model, t, o):
    if t == "Jan":
        return init_store + buy[t, o] == consume[t, o] + store[t, o]
    else:
        return store[months[months.index(t) - 1], o] + buy[t, o] == consume[t, o] + store[t, o]
model.c1 = pyo.Constraint(months, oils, rule = balance)

# Inventory Target (In June)
def inv_target(model, o):
    return store["Jun", o] == target_store
model.c2 = pyo.Constraint(oils, rule = inv_target)

# Refinement Capacity - Total tons of oil consumed cannot exceed capacity

# For Veg-oils

def refinement_cap_veg(model, t):
    return pyo.quicksum(consume[t, o] for o in oils if "VEG" in o) <= veg_cap
model.c3 = pyo.Constraint(months, rule = refinement_cap_veg)

# For Non-Veg-oils

def refinement_cap_non_veg(model, t):
    return pyo.quicksum(consume[t, o] for o in oils if "OIL" in o) <= non_veg_cap
model.c4 = pyo.Constraint(months, rule = refinement_cap_non_veg)

# Hardness - Hardness of produced food must be within tolerances

def hardness_cons(model, t):
    return (min_hardness*produce[t], 
            pyo.quicksum(hardness[o]*consume[t, o] 
                         for o in oils), 
            max_hardness*produce[t])
# model.c5 = pyo.Constraint(months, rule = hardness_cons)

model.hardness_cons = pyo.ConstraintList()

for t in months:
    model.hardness_cons.add(
        min_hardness*produce[t] <= pyo.quicksum(hardness[o]*consume[t, o] 
                                                for o in oils)
        )
    model.hardness_cons.add(
        pyo.quicksum(hardness[o]*consume[t, o] 
                     for o in oils) <= max_hardness*produce[t]
        )

# Mass Conservation

def mass_conservation(model, t):
    return pyo.quicksum(consume[t, o] 
                        for o in oils) == produce[t]
model.c6 = pyo.Constraint(months, rule = mass_conservation)

# Objective Function

def obj_fn(model):
    return (pyo.quicksum(price*produce[t] 
                         for t in months) 
            - pyo.quicksum((cost[t, o]*buy[t, o]) 
                           + inv_cost*store[t, o] 
                           for t in months 
                           for o in oils))
model.obj = pyo.Objective(rule = obj_fn, sense = pyo.maximize)

# Solution

sol = SolverFactory("cplex")
res = sol.solve(model)

# Printing the Solution

print(res)

rows = months[:]
columns = oils[:]

purchase_plan = pd.DataFrame(columns = columns, index = rows, data = 0.0)

for t in months:
    for o in oils:
        purchase_plan.loc[t, o] = round(buy[t, o](), 3)
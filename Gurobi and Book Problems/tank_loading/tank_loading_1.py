import pyomo.environ as pyo
from pyomo.opt import SolverFactory

# Model

model = pyo.ConcreteModel()

# Sets and Params

cap = {
       (1) : 500,
       (2) : 400, 
       (3) : 400,
       (4) : 600, 
       (5) : 600,
       (6) : 900, 
       (7) : 800,
       (8) : 800,
       (9) : 800
       }

liquid_products = {("Benzol"): 1200,
                   ("Butanol"): 700,
                   ("Propanol"): 1000,
                   ("Styrene"): 450,
                   ("THF"): 1200}

model.tanks = pyo.RangeSet(1, 9)
tanks = model.tanks

model.products = pyo.Set(initialize = liquid_products.keys())
products = model.products

filled = {}

for i in tanks:
    if i == 2:
        filled[(i, "Benzol")] = 100
    elif i == 7:
        filled[(i, "THF")] = 300
    else:
        filled[i] = 0

qinit = {
    2 : 100, 
    7 : 300
    }

remaining = liquid_products

for product in liquid_products.keys():
    for tup in filled:
        if filled[tup] and tup[1] == product:
            remaining[product] = liquid_products[product] - filled[tup]

# for l in liquid_products:
#     remaining[l] = liquid_products[l] - pyo.quicksum(cap[t] - qinit[t] 
#                                                      for t in tanks)

# Variables

variable_arcs = []

for l in liquid_products:
    for t in tanks:
        if (t != 2 and t != 7):
            variable_arcs.append((l, t))

# model.load_ = pyo.Var(liquid_products, tanks, within = pyo.Binary)
# load = model.load_

model.load_ = pyo.Var(variable_arcs, within = pyo.Binary)
load = model.load_

# Constraints

def sufficient_capacity(model, l):
    return pyo.quicksum(cap[t]*load[l, t] 
                        for t in tanks if (t != 2 and t != 7)) >= remaining[l]
model.c1 = pyo.Constraint(liquid_products, rule = sufficient_capacity)

def at_most_one(model, t):
    try:    
        if not filled[t] and (t != 2 and t != 7):
            return pyo.quicksum(load[l, t] 
                                for l in liquid_products) <= 1
    except KeyError:
        return pyo.Constraint.Skip
model.c2 = pyo.Constraint(tanks, rule = at_most_one)

# Objective Function

def obj_fn(model):
    return pyo.quicksum(cap[t]*load[l, t] 
                        for l in liquid_products 
                        for t in tanks 
                        if (t != 2 and t != 7))
model.obj = pyo.Objective(rule = obj_fn, sense = pyo.maximize)

# Solution

sol = SolverFactory("cplex")
res = sol.solve(model)

# Prining the Solution

print(res)

filled_after_solving = {l : 0 
                        for l in liquid_products}

remaining_after_solving = remaining

tank_filling = {t : 0 for t in tanks}

for l in liquid_products:
    for t in tanks:
        if (t != 2 and t != 7) and load[l, t]() and load[l, t]() >= 0.9:
            print(f"Product-{l} in Tank-{t}")
            # filled_after_solving[l] += 
            tank_filling[t] += load[l, t]()*remaining_after_solving[l]
            remaining_after_solving[l] -= cap[t]



















import pyomo.environ as pyo, gurobipy as gp
from itertools import product
from pyomo.opt import SolverFactory

# IP-OP matrix for the production of each industry

arcs, inout_prod = gp.multidict({
    ('coal', 'coal'): 0.1,
    ('coal', 'steel'): 0.5,
    ('coal', 'transport'): 0.4,
    ('steel', 'coal'): 0.1,
    ('steel', 'steel'): 0.1,
    ('steel', 'transport'): 0.2,
    ('transport', 'coal'): 0.2,
    ('transport', 'steel'): 0.1,
    ('transport', 'transport'): 0.2
})

# Labour requirements for the production of goods of each industry

labor_prod = dict({'coal': 0.6,
                   'steel': 0.3,
                   'transport': 0.2})

# IP-OP matrix to create extra capacity for each industry

arcs, inout_cap = gp.multidict({
    ('coal', 'coal'): 0.1,
    ('coal', 'steel'): 0.7,
    ('coal', 'transport'): 0.9,
    ('steel', 'coal'): 0.1,
    ('steel', 'steel'): 0.1,
    ('steel', 'transport'): 0.2,
    ('transport', 'coal'): 0.2,
    ('transport', 'steel'): 0.1,
    ('transport', 'transport'): 0.2
})

# Labour requirements to increase capacity of each industry

labor_extra_cap = dict({'coal': 0.4,
                  'steel': 0.2,
                  'transport': 0.1})

# Initial stock, initial capacity and demand of each industry

industries, stock0, capacity0, demand = gp.multidict({
    'coal': [250,300,60],
    'steel': [180,350,60],
    'transport': [200,280,30]
})

# Time Horizons

horizon = [1,2,3,4,5,6]
fiveYears = [1,2,3,4,5]
years2_4 = [2,3,4]

# Computed Parameters

i2h = set(product(industries, horizon))
i2f = set(product(industries, fiveYears))

# Model

model = pyo.ConcreteModel()

# Variables

model.static_prod = pyo.Var(industries, within = pyo.NonNegativeReals)
static_prod = model.static_prod

def prod_bound(model, ind, t):
    if t == 1:
        return (0, 0)
    else:
        return (0, None)

model.prod = pyo.Var(i2h, within = pyo.NonNegativeReals, bounds = prod_bound)
prod = model.prod

model.stock = pyo.Var(i2f, within = pyo.NonNegativeReals)
stock = model.stock

def extra_cap_bound(model, j, t):
    if t <= 2 or t == 6:
        return (0, 0)
    else:
        return (0, None)

model.extra_cap = pyo.Var(i2h, within = pyo.NonNegativeReals, bounds = extra_cap_bound)
extra_cap = model.extra_cap

# Constraints

# Year-1 balance equations

def static_balance(model, i):
    return (static_prod[i] - 
            pyo.quicksum(inout_prod[i, j]*static_prod[j] 
                         for j in industries) == 
            demand[i])
model.c1 = pyo.Constraint(industries, rule = static_balance)

def year_1_balance(model, i):
    return (stock0[i] == 
            pyo.quicksum(inout_prod[i, j]*prod[j, 2] 
                         for j in industries) + 
            demand[i] + 
            pyo.quicksum(inout_cap[i, j]*extra_cap[j, 3] 
                         for j in industries) + 
            stock[i, 1])
model.c2 = pyo.Constraint(industries, rule = year_1_balance)

def year_2_4_balance(model, i, t):
    return (prod[i, t] + stock[i, t-1] == 
            pyo.quicksum(inout_prod[i, j]*prod[j, t+1]  
                         for j in industries) + 
            demand[i] + 
            pyo.quicksum(inout_cap[i, j]*extra_cap[j, t+2] 
                         for j in industries) + 
            stock[i, t]
            )
model.c3 = pyo.Constraint(industries, years2_4, rule = year_2_4_balance)

def year_5_balance(model, i):
    return (prod[i, 5] + stock[i, 4] == 
            pyo.quicksum(inout_prod[i, j]*prod[j, 6] 
                         for j in industries) + 
            demand[i] + 
            stock[i, 5])
model.c4 = pyo.Constraint(industries, rule = year_5_balance)

model.steady_prod = pyo.ConstraintList()

for j in industries:
    model.steady_prod.add(
        prod[j, 6] >= static_prod[j]
        )

# Productive Capacity Constraints

def prod_cap_cons(model, ind, year):
    return (prod[ind, year] - 
            pyo.quicksum(extra_cap[ind, t] 
                         for t in fiveYears 
                         if t <= year) <= 
            capacity0[ind])
model.c5 = pyo.Constraint(i2f, rule = prod_cap_cons)

# Objective Function

def obj_fn(model):
    return (pyo.quicksum(labor_prod[j]*prod[j, t] 
                         for j in industries 
                         for t in fiveYears) + 
            pyo.quicksum(labor_extra_cap[j]*extra_cap[j, t] 
                         for j in industries 
                         for t in fiveYears))
model.obj = pyo.Objective(rule = obj_fn, sense = pyo.maximize)

# Solution

sol = SolverFactory("cplex")
res = sol.solve(model)

# Printing the Solution

print(f"The objective of maximizing the employment results in total manpower utilization : ${model.obj()} Millions.")













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

def extra_cap_bound(model, q, t):
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

model.obj = pyo.Objective(expr = 0, sense = pyo.maximize)

sol = SolverFactory("cplex")
res = sol.solve(model)

for i in industries:
    if (static_prod[i]() > 1e-3):
        dollars_static_prod = '${:,.2f}'.format(static_prod[i]())
        print(f"Generate {dollars_static_prod} million dollars of {i} ")
import pyomo.environ as pyo
from pyomo.opt import SolverFactory

# Model

model = pyo.ConcreteModel()

# Data

materials = [0, 10000, 15000]

critical_liquids = [0, 0.4, 0.2]

demands = {
    "A" : 6000, 
    "B" : 7000, 
    "C" : 9000
    }

sales_price = {
    "A" : 125, 
    "B" : 135, 
    "C" : 155
    }

# Sets

model.components = pyo.RangeSet(1, 2)
components = model.components

model.products = pyo.Set(initialize = demands.keys())
products = model.products

# Variables

model.x = pyo.Var(components, products, within = pyo.NonNegativeReals)
x = model.x

# Csontraints

def demand_cons(model, p):
    return pyo.quicksum(x[c, p] for c in components) >= demands[p]
model.c1 = pyo.Constraint(products, rule = demand_cons)

def component_cons(model, c):
    return pyo.quicksum(x[c, p] 
                        for p in products) <= materials[c]
model.c2 = pyo.Constraint(components, rule = component_cons)

def critical_a(model):
    return (pyo.quicksum(x[c, "A"]*critical_liquids[c] 
                        for c in components) 
            >= 0.3*pyo.quicksum(x[c, "A"] for c in components))
model.c3 = pyo.Constraint(rule = critical_a)

def critical_b(model):
    return (pyo.quicksum(x[c, "B"]*critical_liquids[c] 
                        for c in components) 
            <= 0.3*pyo.quicksum(x[c, "B"] for c in components))
model.c4 = pyo.Constraint(rule = critical_b)

def critical_c(model):
    return x[1, "C"] >= 0.3*x[2, "C"]
model.c5 = pyo.Constraint(rule = critical_c)

def component_cons_2(model, c, p):
    return x[c, p] >= 1000
model.c6 = pyo.Constraint(components, products, rule = component_cons_2)

# Objective Function

def obj_fn(model):
    return pyo.quicksum(x[c, p]*sales_price[p] 
                        for c in components 
                        for p in products)
model.obj = pyo.Objective(rule = obj_fn, sense = pyo.maximize)

# Solution

sol = SolverFactory("cplex", solver_io = "python")
res = sol.solve(model)

# Printing the Solution

print(res)

for c in components:
    for p in products:
        print(f"x[{c, p}] : {x[c, p]()}")
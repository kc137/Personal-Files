import pyomo.environ as pyo
from pyomo.opt import SolverFactory

# Model

model = pyo.ConcreteModel()

# Data

painting = [2000, 1500]

assembly = [2200, 2200]

profits = [2100, 3000]

# Sets

model.types = pyo.RangeSet(1, 2)
types = model.types

model.operations = pyo.Set(initialize = ["P", "A"])
operations = model.operations

# Variables

model.x = pyo.Var(types, within = pyo.NonNegativeReals)
x = model.x

# Constraints

def painting_cons(model):
    return pyo.quicksum(x[t] / painting[t-1] 
                        for t in types) <= 1
model.c1 = pyo.Constraint(rule = painting_cons)

def assembly_cons(model):
    return pyo.quicksum(x[t] / assembly[t-1] 
                        for t in types) <= 1
model.c2 = pyo.Constraint(rule = assembly_cons)

# Objective Function

def obj_fn(model):
    return pyo.quicksum(x[t]*profits[t-1] 
                        for t in types)
model.obj = pyo.Objective(rule = obj_fn, sense = pyo.maximize)

# Solution

sol = SolverFactory("cplex", solver_io = "python")
res = sol.solve(model)

# Printing the Solution

print(res)

for t in types:
    print(f"Total type-{t} of assembled : {x[t]()}")
import pyomo.environ as pyo
from pyomo.opt import SolverFactory

# Model

model = pyo.ConcreteModel()

# Data

supply = [5000, 6000, 2500]

demand = [6000, 4000, 2000, 1500]

cost_matrix = [
    [30, 20, 70, 60],
    [70, 50, 20, 30],
    [20, 50, 40, 50]
]

# Sets

model.s_cities = pyo.RangeSet(1, len(supply))
s_cities = model.s_cities

model.d_cities = pyo.RangeSet(1, len(demand))
d_cities = model.d_cities

# Variables

model.x = pyo.Var(s_cities, d_cities, within = pyo.NonNegativeReals)
x = model.x

# Constraints

def supply_cons(model, s):
    return pyo.quicksum(x[s, d] for d in d_cities) == supply[s-1]
model.c1 = pyo.Constraint(s_cities, rule = supply_cons)

def demand_cons(model, d):
    return pyo.quicksum(x[s, d] for s in s_cities) == demand[d-1]
model.c2 = pyo.Constraint(d_cities, rule = demand_cons)

# Objective Function

def obj_fn(model):
    return pyo.quicksum(x[s, d]*cost_matrix[s-1][d-1] 
                        for s in s_cities 
                        for d in d_cities)
model.obj = pyo.Objective(rule = obj_fn, sense = pyo.minimize)

# Solution

sol = SolverFactory("cplex", solver_io = "python")
res = sol.solve(model)

# Printing the Solution

print(res)

for s in s_cities:
    for d in d_cities:
        print(f"The amount supplied from city-{s} to city-{d} : {x[s, d]()}")
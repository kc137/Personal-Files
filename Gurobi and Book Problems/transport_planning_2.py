import pyomo.environ as pyo
from pyomo.opt import SolverFactory

path = "F:\\Solvers\\CPLEX_2211\\cplex\\bin\\x64_win64\\cplex.exe"

# Model

model = pyo.ConcreteModel()

# Data

cost_matrix = [
    [50, 60, 30], 
    [60, 40, 20], 
    [40, 70, 30]
    ]

demand = [5, 4, 3]

supply = [8, 5, 3]

# Sets

# model.o_cities = pyo.RangeSet(1, 3)
# o_cities = model.o_cities

# model.d_cities = pyo.RangeSet(1, 3)
# d_cities = model.d_cities

model.o_cities = pyo.Set(initialize = ["X", "Y", "Z"])
o_cities = model.o_cities

for o_i, o in enumerate(o_cities):
    print(o_i, o)

model.d_cities = pyo.Set(initialize = ["A", "B", "C"])
d_cities = model.d_cities

# Variables

model.x = pyo.Var(o_cities, d_cities, within = pyo.NonNegativeIntegers)
x = model.x

model.z = pyo.Var(o_cities, within = pyo.NonNegativeIntegers)
z = model.z

# Constraints

def supply_cons(model, s):
    i_s = list(o_cities).index(s)
    return pyo.quicksum(x[s, d] 
                        for d in d_cities) + z[s] <= supply[i_s]
model.c1 = pyo.Constraint(o_cities, rule = supply_cons)

def demand_cons(model, d):
    i_d = list(d_cities).index(d)
    return pyo.quicksum(x[s, d] 
                        for s in o_cities) >= demand[i_d]
model.c2 = pyo.Constraint(d_cities, rule = demand_cons)

# Objective Function

def obj_fn(model):
    return pyo.quicksum(x[s, d]*cost_matrix[i_s][i_d] 
                        for i_s, s in enumerate(o_cities) 
                        for i_d, d in enumerate(d_cities))
model.obj = pyo.Objective(rule = obj_fn, sense = pyo.minimize)

# Solution

# sol = SolverFactory("cplex", executable = path)
sol = SolverFactory("cplex")
res = sol.solve(model)

# Printing the Solution

print(res)

for s in o_cities:
    for d in d_cities:
        print(f"Machines transferred from City-{s} to City-{d} : {round(x[s, d]())}")
import pyomo.environ as pyo, pandas as pd
from pyomo.opt import SolverFactory
from collections import defaultdict

with open("cctv_1.dat", "r") as data:
    
    connections = []
    positions = []
    pos_str = []
    
    lines = data.read().splitlines()
    
    for line in lines[1:59]:
        line = line.replace("(", "").replace(")", "").replace("[", "").replace("]", "")
        line = line.split()
        connections.append((int(line[0]), int(line[1])))
    
    for line in lines[60:]:
        line = line.replace("POS: ", "").replace("[", "").replace("]", "")
        pos_str += line.split()
        
    for i in range(0, len(pos_str), 2):
        positions.append((int(pos_str[i]), int(pos_str[i+1])))

# adj_list = defaultdict(list)

# for i, j in connections:
#     adj_list[i].append(j)
#     adj_list[j].append(i)
    
# Model

model = pyo.ConcreteModel()

# Sets and Params

model.cities = pyo.RangeSet(1, len(positions))
cities = model.cities

# Variables

model.x = pyo.Var(cities, within = pyo.Binary)
x = model.x

# Constraints

def coverage_cons(model, c1, c2):
    return x[c1] >= (1 - x[c2])
model.c1 = pyo.Constraint(connections, rule = coverage_cons)

# Objective Function

def obj_fn(model):
    return pyo.quicksum(x[c] for c in cities)
model.obj = pyo.Objective(rule = obj_fn, sense = pyo.minimize)

# Solution

sol = SolverFactory("cplex")
res = sol.solve(model)

# Printing the Solution

print(res)

for c in model.cities:
    if x[c]() and x[c]() >= 0.9:
        print(f"Camera is installed at City-{c}")


"""
The solution is opposite when maximization occurs

return x[c1] <= (1 - x[c2])
model.obj = pyo.Objective(rule = obj_fn, sense = pyo.maximize)
if x[c]() and x[c]() <= 0.1:

"""











import pyomo.environ as pyo, time
from pyomo.opt import SolverFactory

start = time.time()

model = pyo.ConcreteModel()

distance_arcs = {}

with open("shortest_path.txt", "r") as data:
    lines = data.read().splitlines()
    for line in lines:
        arc = line.split()
        n1, n2, d = int(arc[0]), int(arc[1]), int(arc[2])
        distance_arcs[(n1, n2)] = d

# Sets and Parameters

model.cities = pyo.RangeSet(1, 7)
model.m_cities = pyo.RangeSet(2, 6)

model.arcs = pyo.Set(initialize = distance_arcs.keys())

model.distances = pyo.Param(model.arcs, within = pyo.Any, 
                            initialize = {
                                arc : distance_arcs[arc] 
                                for arc in model.arcs
                                })

distances = model.distances

model.fromp = {n : [] for n in model.cities}
model.top = {n : [] for n in model.cities}

for arc in model.arcs:
    model.fromp[arc[0]].append(arc[1])
    model.top[arc[1]].append(arc[0])

# Variables

model.x = pyo.Var(model.arcs, within = pyo.Binary)
x = model.x

# Constraints

def initial_flow(model):
    return sum(x[model.cities.at(1), j] for j in model.fromp[model.cities.at(1)]) == 1
model.c1 = pyo.Constraint(rule = initial_flow)

def final_flow(model):
    return sum(x[i, model.cities.at(-1)] for i in model.top[model.cities.at(-1)]) == 1
model.c2 = pyo.Constraint(rule = final_flow)

def equal_flow(model, i):
    return sum(x[i, j] for j in model.fromp[i]) == sum(x[j, i] for j in model.top[i])
model.c3 = pyo.Constraint(model.m_cities, rule = equal_flow)

# Objective Function

def obj_fn(model):
    return sum(x[i, j]*distances[i, j] 
               for i, j in model.arcs)
model.obj = pyo.Objective(rule = obj_fn, sense = pyo.minimize)

# Solution

sol = SolverFactory("cplex")
res = sol.solve(model)

# Printing the Results

print("Path :", end = " ")

for p1, p2 in model.arcs:
    if x[p1, p2]():
        if p1 == model.cities.at(1):
            print(f"{p1} --> {p2}", end = " ")
        else:
            print(f"--> {p2}", end = " ")
        
print(f"\nTotal distance covered : {model.obj()}")

print(f"Total Time taken by Solver : {round(time.time() - start, 4)} sec.")






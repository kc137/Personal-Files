import pyomo.environ as pyo, random, matplotlib.pyplot as plt, matplotlib
import math
from pyomo.opt import SolverFactory
matplotlib.use("tkagg")

# Model

model = pyo.ConcreteModel()

# Big-M
M = 100000

N = 17
locations = [*range(1, N+1)]

K = 6
vehicles = [*range(1, K+1)]

points = [(0, 0)]
points += [(random.randint(0, 50), random.randint(0, 50)) for _ in range(N-1)]

# for x, y in points:
#     plt.scatter(x, y)

time = {(i, j) : math.hypot(points[i-1][0] - points[j-1][0], 
                            points[i-1][1] - points[j-1][1]) 
        for i in locations 
        for j in locations}

# Sets and Parameters

model.N = pyo.RangeSet(1, N)
model.C = pyo.RangeSet(2, N)

# Variables

model.x = pyo.Var(model.N, model.N, within = pyo.Binary)
x = model.x

model.q = pyo.Var(model.N, within = pyo.NonNegativeReals, bounds = (0, 120))
q = model.q

# Constraints

# Each vehicle travel only once

def once(model, j):
    return pyo.quicksum(x[i, j] for i in model.N if i != j) == 1
model.c1 = pyo.Constraint(model.C, rule = once)

def flow(model, j):
    return (pyo.quicksum(x[i, j] for i in model.N if i != j) 
            == pyo.quicksum(x[j, i] for i in model.N if i != j))
model.c2 = pyo.Constraint(model.C, rule = flow)

# def flow(model, i):
#     return (pyo.quicksum(x[i, j] for j in model.C if i != j) 
#             == pyo.quicksum(x[j, i] for j in model.C if i != j))
# model.c2 = pyo.Constraint(model.C, rule = flow)

def time_cons(model, i, j):
    if i != j:
        return q[i] + time[i, j] + time[j, 1]*x[j, 1] <= q[j] + 120*(1 - x[i, j])
    else:
        return pyo.Constraint.Skip
model.c3 = pyo.Constraint(model.N, model.C, rule = time_cons)

def total_trips(model):
    return pyo.quicksum(x[1, j] for j in model.C) >= 1
model.c4 = pyo.Constraint(rule = total_trips)

# model.max_time = pyo.ConstraintList()

# for j in model.C:
#     model.max_time.add(
#         q[j] <= 120
#         )

# Objective Function

def obj_fn(model):
    return pyo.quicksum(x[1, j] for j in model.C)
    # return pyo.quicksum(x[i, j]*time[i, j] 
    #                     for i in locations 
    #                     for j in locations if i != j)
model.obj = pyo.Objective(rule = obj_fn, sense = pyo.minimize)

# Solution

sol = SolverFactory("cplex")
sol.options["timelimit"] = 10
res = sol.solve(model)

# Printing the Results

print(res)

edges = []
for i in model.N:
    for j in model.N:
        if x[i, j]() and x[i, j]() >= 0.9:
            print(f"x[{i}, {j}] = {x[i, j]()}")
            edges.append((i, j))

origins = []

for j in model.C:
    if x[1, j]() and x[1, j]() >= 0.9:
        origins.append((1, j))
    print(f"q[{j}] = {q[j]()}")









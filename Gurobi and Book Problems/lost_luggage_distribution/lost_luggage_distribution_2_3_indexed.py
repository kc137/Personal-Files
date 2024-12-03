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
model.V = pyo.RangeSet(1, K)

# Variables

model.x = pyo.Var(model.N, model.N, model.V, within = pyo.Binary)
x = model.x

model.u = pyo.Var(model.N, model.V, within = pyo.NonNegativeReals)
u = model.u

# Constraints

def once(model, j):
    return pyo.quicksum(x[i, j, k] 
                        for i in model.N 
                        for k in model.V 
                        if i != j) == 1
model.c1 = pyo.Constraint(model.C, rule = once)

def flow(model, j, k):
    return pyo.quicksum(x[i, j, k] 
                        for i in model.N 
                        if i != j) == \
        pyo.quicksum(x[j, i, k] 
                     for i in model.N 
                     if i != j)
model.c2 = pyo.Constraint(model.C, model.V, rule = flow)

def initial_tour(model, k):
    return pyo.quicksum(x[1, j, k] 
                        for j in model.C) <= 1
model.c3 = pyo.Constraint(model.V, rule = initial_tour)

def max_distance(model, k):
    return pyo.quicksum(x[i, j, k]*time[i, j] 
                        for i in model.N 
                        for j in model.C 
                        if i != j) <= 120
model.c4 = pyo.Constraint(model.V, rule = max_distance)

model.sub_tour = pyo.ConstraintList()

for k in model.V:
    for i in model.C:
        for j in model.C:
            if i != j:
                model.sub_tour.add(
                    u[i, k] - u[j, k] + N*(x[i, j, k]) <= N-1
                    )

# Objective Function

def obj_fn(model):
    return pyo.quicksum(x[1, j, k] 
                        for j in model.C 
                        for k in model.V)
model.obj = pyo.Objective(rule = obj_fn, sense = pyo.minimize)

# Solution

sol = SolverFactory("cplex")
sol.options["timelimit"] = 100
res = sol.solve(model)

# Printing the Solution

print(res)

for i in model.N:
    for j in model.N:
        for k in model.V:
            if x[i, j, k]() and x[i, j, k]() >= 0.9:
                print(f"x[{i}, {j}, {k}] = {x[i, j, k]()}")

"""
100 s of solution.
x[1, 6, 5] = 1.0
x[1, 10, 4] = 1.0
x[1, 11, 1] = 1.0
x[2, 12, 4] = 1.0
x[3, 8, 5] = 1.0
x[4, 1, 5] = 1.0
x[5, 4, 5] = 1.0
x[6, 9, 5] = 1.0
x[7, 1, 4] = 1.0
x[8, 5, 5] = 1.0
x[9, 3, 5] = 1.0
x[10, 16, 4] = 1.0
x[11, 14, 1] = 1.0
x[12, 7, 4] = 1.0
x[13, 1, 1] = 1.0
x[14, 15, 1] = 1.0
x[15, 13, 1] = 1.0
x[16, 17, 4] = 1.0
x[17, 2, 4] = 1.0
"""









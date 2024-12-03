import pyomo.environ as pyo, numpy as np, matplotlib.pyplot as plt
from pyomo.opt import SolverFactory
from scipy.spatial.distance import pdist, squareform

N = 30
np.random.seed(12)
coords = np.random.random((N, 2))
D = squareform(pdist(coords))

# Model

model = pyo.ConcreteModel()

# Sets and Params

model.M = pyo.RangeSet(1, N)

model.arcs = pyo.Set(initialize = [(i, j) 
                                   for i in model.M 
                                   for j in model.M 
                                   if i != j])

model.distance_matrix = pyo.Param(model.arcs, 
                                  initialize = {(i, j) : D[i-1, j-1] 
                                  for (i, j) in model.arcs})
distance_matrix = model.distance_matrix

# Variables

model.x = pyo.Var(model.arcs, within = pyo.Binary)
x = model.x

model.u = pyo.Var(model.M, within = pyo.NonNegativeReals)
u = model.u

# Constraints

def in_once(model, j):
    return pyo.quicksum(x[:, j]) == 1
model.c1 = pyo.Constraint(model.M, rule = in_once)

def out_once(model, i):
    return pyo.quicksum(x[i, :]) == 1
model.c2 = pyo.Constraint(model.M, rule = out_once)

def sub_tour_mtz(model, i, j):
    if i != model.M.first() and j != model.M.first():
        return u[i] - u[j] + N*(x[i, j]) <= N - 1
    else:
        return pyo.Constraint.Skip
model.c3 = pyo.Constraint(model.arcs, rule = sub_tour_mtz)

# Objective Function

def obj_fn(model):
    return pyo.quicksum(distance_matrix[i, j]*x[i, j] 
                        for i, j in model.arcs)
model.obj = pyo.Objective(rule = obj_fn, sense = pyo.minimize)

# Solution

sol = SolverFactory("cplex")
res = sol.solve(model)

# Printing the Solution

print(res)

arcs = []

for i, j in model.arcs:
    if x[i, j]() and x[i, j]() >= 0.9:
        arcs.append((i, j))
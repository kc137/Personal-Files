import numpy as np, matplotlib.pyplot as plt
from ortools.sat.python import cp_model as cp
from cvrp_2_indexed_data import matrix, NV, coords, demands, capacity as Q
from scipy.spatial.distance import pdist, squareform

DIST = np.round(squareform(pdist(coords)), 4)

locations = range(len(DIST))

distance_matrix = {}

for i in locations:
    for j in locations:
        distance_matrix[(i, j)] = DIST[i, j]

# Model

model = cp.CpModel()

# Variables

x = {}
for i in locations:
    for j in locations:
        x[i, j] = model.NewBoolVar("")

q = {}
for j in locations:
    q[j] = model.NewIntVar(0, Q, "")
        
# Constraints

for j in locations[1:]:
    model.add(
        sum(x[i, j] for i in locations if i != j) 
        == sum(x[j, i] for i in locations if i != j)
        )

for j in locations[1:]:
    model.add(sum(x[i, j] for i in locations if i != j) == 1)

for i in locations:
    for j in locations[1:]:
        if i != j:
            model.add(
                q[i] + demands[j] <= q[j] + Q*(1 - x[i, j])
                )
        
model.add(sum(x[0, j] for j in locations[1:]) >= 1)
model.add(sum(x[0, j] for j in locations[1:]) <= NV)

min_obj = sum(x[i, j]*distance_matrix[i, j] 
              for i in locations
              for j in locations 
              if i != j)
model.Minimize(min_obj)

solver = cp.CpSolver()
solver.parameters.num_search_workers = 8
solver.parameters.max_time_in_seconds = 15
res = solver.solve(model)

print(solver.ResponseStats())



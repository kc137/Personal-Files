import numpy as np, matplotlib.pyplot as plt, datetime
from ortools.math_opt.python import mathopt
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

model = mathopt.Model()

# Variables

x = {}
for i in locations:
    for j in locations:
        x[i, j] = model.add_binary_variable()

q = {}
for j in locations:
    q[j] = model.add_integer_variable(lb = 0, ub = Q)
        
# Constraints

for j in locations[1:]:
    model.add_linear_constraint(
        sum(x[i, j] for i in locations if i != j) 
        == sum(x[j, i] for i in locations if i != j)
        )

for j in locations[1:]:
    model.add_linear_constraint(sum(x[i, j] for i in locations if i != j) == 1)

for i in locations:
    for j in locations[1:]:
        if i != j:
            model.add_linear_constraint(
                q[i] + demands[j] <= q[j] + Q*(1 - x[i, j])
                )
        
model.add_linear_constraint(sum(x[0, j] for j in locations[1:]) >= 1)
model.add_linear_constraint(sum(x[0, j] for j in locations[1:]) == NV)

min_obj = sum(x[i, j]*distance_matrix[i, j] 
              for i in locations
              for j in locations 
              if i != j)
model.minimize(min_obj)

params = mathopt.SolveParameters(
    time_limit = datetime.timedelta(seconds = 5), 
    threads = 8, 
    enable_output = False)

res = mathopt.solve(model, mathopt.SolverType.CP_SAT, params = params)

# print(res)

arcs = []
arc_finder = {l : [] for l in locations}

for i in locations:
    for j in locations:
        if i != j and res.variable_values()[x[i, j]]:
            arcs.append((i, j))
            arc_finder[i].append(j)

if res.termination.reason == mathopt.TerminationReason.FEASIBLE:
    print("Feasible")

if res.termination.reason == mathopt.TerminationReason.OPTIMAL:
    print("Optimal")

# print(res)
print(arcs)



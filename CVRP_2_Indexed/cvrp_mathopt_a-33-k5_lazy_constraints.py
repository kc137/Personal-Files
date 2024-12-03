import numpy as np, matplotlib.pyplot as plt, datetime
from ortools.math_opt.python import mathopt
from ortools.sat.python import cp_model as cp
from cvrp_2_indexed_data import matrix, NV, coords, demands, capacity as Q
from scipy.spatial.distance import pdist, squareform
from itertools import permutations

DIST = np.round(squareform(pdist(coords)), 4)

locations = range(len(DIST))

N = len(locations)

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

# for i in locations:
#     for j in locations[1:]:
#         if i != j:
#             model.add_linear_constraint(
#                 x[i, j]*demands[j] <= Q
#                 )
        
model.add_linear_constraint(sum(x[0, j] for j in locations[1:]) >= 1)
model.add_linear_constraint(sum(x[0, j] for j in locations[1:]) == NV)

min_obj = sum(x[i, j]*distance_matrix[i, j] 
              for i in locations
              for j in locations 
              if i != j)
model.minimize(min_obj)

arc_finder = {l : [] for l in locations}

def arcs_finder():
    arcs = []
    for i in locations:
        for j in locations:
            if i != j and res.variable_values()[x[i, j]]:
                arcs.append((i, j))
                arc_finder[i].append(j)
    return arcs

def get_subtours(sol):
    subtours = []
    LS = len(sol)
    unvisited = [NV] + [1 for _ in range(N-1)]
    
    while LS > 0:
        subtour = []
        subtours.append(subtour)
        for i in range(N):
            if unvisited[i]:
                start = i
                break
        
        while True:
            subtour.append(start)
            if unvisited[start]:
                unvisited[start] -= 1
                LS -= 1
            next_node = next((j for (i, j) in sol if i == start and unvisited[j]), None)
            
            if next_node == locations[0] or not next_node or not unvisited[next_node]:
                break
            start = next_node
    print(subtours)
    return subtours

def subtour_elim():
    if (res.termination.reason == mathopt.TerminationReason.OPTIMAL 
        or res.termination.reason == mathopt.TerminationReason.FEASIBLE):
        
        arcs = arcs_finder()
        subtours = get_subtours(arcs)
        
        if len(subtours) > NV:
            print("No")
            for tour in subtours:
                model.add_linear_constraint(
                    sum(x[i, j] 
                        for (i, j) in permutations(tour, 2)) 
                    <= len(tour) - 1
                    )

params = mathopt.SolveParameters(
    time_limit = datetime.timedelta(seconds = 5), 
    threads = 8, 
    enable_output = False)

res = mathopt.solve(model, mathopt.SolverType.CP_SAT, 
                    params = params, 
                    cb = subtour_elim)

# print(res)
print(arcs_finder())

print(get_subtours(arcs_finder()))
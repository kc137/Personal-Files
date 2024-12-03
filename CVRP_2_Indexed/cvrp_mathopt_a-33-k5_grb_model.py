import numpy as np, matplotlib.pyplot as plt
from ortools.sat.python import cp_model as cp
from cvrp_2_indexed_data import matrix, NV, coords, demands, capacity as Q
from scipy.spatial.distance import pdist, squareform
from itertools import permutations, combinations

DIST = np.round(squareform(pdist(coords, metric = "euclidean")), 4)
N = len(DIST)

locations = [*range(len(DIST))]

vans = [*range(NV)]

distance_matrix = {}

for i in locations:
    for j in locations:
        if i != j:
            distance_matrix[(i, j)] = DIST[i, j]

# Model

model = cp.CpModel()

# Variables

x = {}
for i in locations:
    for j in locations:
        for k in vans:
            if i != j:
                x[i, j, k] = model.NewBoolVar("")

y = {}
for j in locations:
    for k in vans:
        y[j, k] = model.NewBoolVar("")
        

z = {}
for k in vans:
    z[k] = model.NewBoolVar("")
        
# Constraints

# Visit Customer must be <= van used

for i in locations[1:]:
    for k in vans:
        model.add(
            y[i, k] <= z[k]
            )

# Visit Customer Once

for j in locations[1:]:
    model.add(
        sum(y[j, k] for k in vans) == 1
        )

# Depot Constraint

for k in vans:
    model.add(
        y[0, k] == z[k]
        )

# Arrival Constraint

for j in locations:
    for k in vans:
        model.add(
            sum(x[i, j, k] for i in locations if i != j) == y[j, k]
            )

# Departing Constraint

for j in locations:
    for k in vans:
        model.add(
            sum(x[j, i, k] for i in locations if i != j) == y[j, k]
            )

# Demand Constraint

for k in vans:
    model.add(
        sum(y[j, k]*demands[j] 
            for j in locations[1:]) <= Q
        )
    
# STE Constraints

# tour = locations[1:]
# for k in vans:
#     model.add(
#         sum(x[i, j, k] for i, j in permutations(tour, 2)) 
#         <= len(tour) - 1
#         )

# for r in range(2, N + 1):
#     for s in combinations(locations[1:], r):
#         model.add(
#             sum(x[i, j, k]
#                 for i in s 
#                 for j in s if i != j
#                 for k in vans
#             ) <= len(s) - 1
#         )
    
# Objective Function

min_obj = sum(x[i, j, k]*distance_matrix[i, j] 
              for i in locations
              for j in locations 
              for k in vans 
              if i != j)
model.Minimize(min_obj)

def get_subtours(edges):
    subtours = []
    LS = len(edges)
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
            next_node = next((j for i, j in edges if i == start and unvisited[j]), None)
            
            if next_node == locations[0] or not next_node or not unvisited[next_node]:
                break
            start = next_node
    # print(subtours)
    return subtours

def subtour_elim():
    arcs = get_arcs()
    subtours = get_subtours(arcs)
    if len(subtours) > NV:
        tour = subtours[-1]
        for k in vans:
            model.add(
                sum(x[i, j, k] for i, j in permutations(tour, 2)) 
                <= len(tour) - 1
                )
    return
    

solver = cp.CpSolver()
solver.parameters.num_search_workers = 8
solver.parameters.max_time_in_seconds = 10
res = solver.solve(model)

print(solver.ResponseStats())

# def get_arcs():
#     arcs = []
    
#     for i in locations:
#         for j in locations:
#             for k in vans:
#                 if i != j and solver.value(x[i, j, k]) >= 0.9:
#                     arcs.append((i, j))
#     return arcs

# # print(arcs)

# subtours = get_subtours(get_arcs())

# # iteration = 1
# # while len(subtours) > NV:
# #     solver = cp.CpSolver()
# #     solver.parameters.num_search_workers = 8
# #     solver.parameters.max_time_in_seconds = 5
# #     res = solver.solve(model)
# #     arcs = get_arcs()
# #     subtours = get_subtours(arcs)
# #     subtour_elim()
# #     print(f"Iteration-{iteration} : {subtours}")
# #     iteration += 1

# print(subtours)



import numpy as np, matplotlib.pyplot as plt
from ortools.sat.python import cp_model as cp
from ortools.sat.python import swig_helper
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

# for i in locations:
#     for j in locations[1:]:
#         if i != j:
#             model.add(
#                 q[i] + demands[j] <= q[j] + Q*(1 - x[i, j])
#                 )
        
model.add(sum(x[0, j] for j in locations[1:]) >= 1)
model.add(sum(x[0, j] for j in locations[1:]) == NV)

min_obj = sum(x[i, j]*distance_matrix[i, j] 
              for i in locations
              for j in locations 
              if i != j)
model.Minimize(min_obj)

arc_finder = {l : [] for l in locations}

def arcs_finder():
    arcs = []
    for i in locations:
        for j in locations:
            if i != j and solver.value(x[i, j]):
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
    # print(subtours)
    return subtours

def subtour_elim():
    if (res == model.OPTIMAL or res == model.FEASIBLE):
        
        arcs = arcs_finder()
        subtours = get_subtours(arcs)
        
        if len(subtours) > NV:
            # print("No")
            for tour in subtours:
                model.add_linear_constraint(
                    sum(x[i, j] 
                        for (i, j) in permutations(tour, 2)) 
                    <= len(tour) - 1
                    )

class Callback(cp.CpSolverSolutionCallback):
    
    def __init__(self, model, x, q):
        cp.CpSolverSolutionCallback.__init__(self)
        self.model = model
        self.x = x
        self.q = q
    
    def on_solution_callback(self):
        print("Cool")
        for i in locations:
            for j in locations[1:]:
                if i != j:
                    self.model.add(
                        self.q[i] + demands[j] <= self.q[j] + Q*(1 - self.x[i, j])
                        )
        return False
        

my_callback = Callback(model, x, q)

solver = cp.CpSolver()
solver.parameters.num_search_workers = 8
solver.parameters.max_time_in_seconds = 5
res = solver.solve(model, my_callback)

# print(solver.ResponseStats())

print(arcs_finder())

print(get_subtours(arcs_finder()))



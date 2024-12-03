import gurobipy as gp, math, random
from gurobipy import GRB
from itertools import permutations

N = 17
locations = [*range(N)]

NV = 4
vans = [*range(NV)]

distance_matrix = [
        # fmt: off
      [0, 548, 776, 696, 582, 274, 502, 194, 308, 194, 536, 502, 388, 354, 468, 776, 662],
      [548, 0, 684, 308, 194, 502, 730, 354, 696, 742, 1084, 594, 480, 674, 1016, 868, 1210],
      [776, 684, 0, 992, 878, 502, 274, 810, 468, 742, 400, 1278, 1164, 1130, 788, 1552, 754],
      [696, 308, 992, 0, 114, 650, 878, 502, 844, 890, 1232, 514, 628, 822, 1164, 560, 1358],
      [582, 194, 878, 114, 0, 536, 764, 388, 730, 776, 1118, 400, 514, 708, 1050, 674, 1244],
      [274, 502, 502, 650, 536, 0, 228, 308, 194, 240, 582, 776, 662, 628, 514, 1050, 708],
      [502, 730, 274, 878, 764, 228, 0, 536, 194, 468, 354, 1004, 890, 856, 514, 1278, 480],
      [194, 354, 810, 502, 388, 308, 536, 0, 342, 388, 730, 468, 354, 320, 662, 742, 856],
      [308, 696, 468, 844, 730, 194, 194, 342, 0, 274, 388, 810, 696, 662, 320, 1084, 514],
      [194, 742, 742, 890, 776, 240, 468, 388, 274, 0, 342, 536, 422, 388, 274, 810, 468],
      [536, 1084, 400, 1232, 1118, 582, 354, 730, 388, 342, 0, 878, 764, 730, 388, 1152, 354],
      [502, 594, 1278, 514, 400, 776, 1004, 468, 810, 536, 878, 0, 114, 308, 650, 274, 844],
      [388, 480, 1164, 628, 514, 662, 890, 354, 696, 422, 764, 114, 0, 194, 536, 388, 730],
      [354, 674, 1130, 822, 708, 628, 856, 320, 662, 388, 730, 308, 194, 0, 342, 422, 536],
      [468, 1016, 788, 1164, 1050, 514, 514, 662, 320, 274, 388, 650, 536, 342, 0, 764, 194],
      [776, 868, 1552, 560, 674, 1050, 1278, 742, 1084, 810, 1152, 274, 388, 422, 764, 0, 798],
      [662, 1210, 754, 1358, 1244, 708, 480, 856, 514, 468, 354, 844, 730, 536, 194, 798, 0],
    ]

demands = [0, 1, 1, 2, 4, 2, 4, 8, 8, 1, 2, 1, 2, 4, 4, 8, 8]
vehicle_capacities = [15, 15, 15, 15]

distances = {(i, j) : distance_matrix[i][j] 
             for i in locations 
             for j in locations 
             if i != j}

model = gp.Model("Lost Luggage Dist")

# Variables

x = model.addVars(distances.keys(), vans, vtype = GRB.BINARY)

# Constraints

# Once

once_cons = model.addConstrs(x.sum("*", j, "*") == 1
                 for j in locations[1:] 
                 )

flow_cons = model.addConstrs(x.sum("*", j, k) == x.sum(j, "*", k) 
                             for j in locations[1:] 
                             for k in vans)

# trips_cons_1 = model.addConstrs(x.sum(i, "*", "*") >= 1
#                                 for i in locations 
#                                 )

trips_cons = model.addConstrs(x.sum(0, "*", "*") == NV
                                for i in locations 
                                )

cap_cons = model.addConstrs(gp.quicksum(x[i, j, k]*demands[j] 
                                        for i in locations 
                                        for j in locations[1:] 
                                        if i != j) <= vehicle_capacities[k]
                            for k in vans)

model.ModelSense = GRB.MINIMIZE
model.setObjective(gp.quicksum(x[i, j, k]*distances[i, j] 
                                for i, j in distances.keys() 
                                for k in vans))

# Callback - use lazy constraints to eliminate sub-tours
def subtourelim(model, where):
    if where == GRB.Callback.MIPSOL:
        # make a list of edges selected in the solution
        vals = model.cbGetSolution(model._x)
        selected = gp.tuplelist((i,j) for i, j, k in model._x.keys()
                                if vals[i, j, k] > 0.5)
        print(selected)
        # find the shortest cycle in the selected edge list
        tour = subtour(selected)
        print(tour)
        if len(tour) < N: 
            for k in vans:
                model.cbLazy(gp.quicksum(model._x[i, j, k]
                                         for i, j in permutations(tour, 2))
                             <= len(tour)-1)


# Given a tuplelist of edges, find the shortest subtour not containing depot (0)
def subtour(edges):
    unvisited = list(range(1, N))
    cycle = range(N+1)  # initial length has 1 more city
    while unvisited:
        thiscycle = []
        neighbors = unvisited
        while neighbors:
            current = neighbors[0]
            thiscycle.append(current)
            if current != 0:
                unvisited.remove(current)
            neighbors = [j for i, j in edges.select(current, '*')
                         if j == 0 or j in unvisited]
        if 0 not in thiscycle and len(cycle) > len(thiscycle):
            cycle = thiscycle
    return cycle

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

def subtour_elim(model, where):
    if where == GRB.Callback.MIPSOL:
        
        vals = model.cbGetSolution(model._x)
        selected = gp.tuplelist([(i,j) for i, j, k in model._x.keys()
                                if vals[i, j, k] > 0.5])
        
        subtours = get_subtours(selected)
        print(selected)
        print(subtours)
        if len(subtours) > NV:
            # min_len = N
            # for mini_tour in subtours[NV:]:
            #     if len(mini_tour) < min_len:
            #         tour = mini_tour
            #         min_len = len(mini_tour)
            tour = subtours[-1]
            print(tour)
            for k in vans:
                model.cbLazy(
                    gp.quicksum(
                        model._x[i, j, k] 
                        for i, j in permutations(tour, 2)) 
                    <= len(tour) - 1
                    )


# Run optimization engine

model._x = x
model.Params.LazyConstraints = 1

model.optimize(subtour_elim)

arcs = []

for i in locations:
    for j in locations:
        for k in vans:
            if i != j and x[i, j, k].X >= 0.9:
                arcs.append((i, j))
            
# print(get_subtours(arcs))

subtours = get_subtours(arcs)

# print(subtours)

new_arcs = [(0, 7), (0, 8), (0, 10), (0, 13), (1, 3), (2, 6), (3, 4), (4, 0), (5, 0), (6, 5), (7, 1), (8, 2), (9, 0), (10, 16), (11, 12), (12, 0), (13, 15), (14, 9), (15, 11), (16, 14)]

print(get_subtours(new_arcs))



import sys
import math
import random
from itertools import permutations
import gurobipy as gp
from gurobipy import GRB

# tested with Python 3.7.0 & Gurobi 9.1.0

# number of locations, including the depot. The index of the depot is 0
N = 17
locations = [*range(N)]

# number of vans
K = 4
vans = [*range(K)]

# Create n random points
# Depot is located at (0,0) coordinates
random.seed(1)
points = [(0, 0)]
points += [(random.randint(0, 50), random.randint(0, 50)) for i in range(N-1)]

# points = [(0, 0),
#  (2, 49),
#  (20, 39),
#  (43, 35),
#  (47, 44),
#  (13, 11),
#  (19, 27),
#  (34, 10),
#  (3, 45),
#  (42, 15),
#  (16, 49),
#  (4, 43),
#  (28, 27),
#  (35, 16),
#  (34, 28),
#  (34, 29),
#  (0, 25)]

# Dictionary of Euclidean distance between each pair of points
# Assume a speed of 60 km/hr, which is 1 km/min. Hence travel time = distance

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

time = {(i, j): distance_matrix[i][j]
        for i in locations for j in locations if i != j}

demands = [0, 1, 1, 2, 4, 2, 4, 8, 8, 1, 2, 1, 2, 4, 4, 8, 8]
    
m = gp.Model('lost_luggage_distribution')

# Create variables: 

# x =1, if van  k  visits and goes directly from location  i  to location  j 
x = m.addVars(time.keys(), vans, vtype=GRB.BINARY, name='FromToBy')

# y = 1, if customer i is visited by van k
y = m.addVars(locations, vans, vtype=GRB.BINARY, name='visitBy')

# Number of vans used is a decision variable
z = m.addVars(vans, vtype=GRB.BINARY, name='used')

# Travel time per van
t = m.addVars(vans, ub=15, name='demand')

# Maximum travel time
s = m.addVar(name='maxTravelTime')

# Van utilization constraint

visitCustomer = m.addConstrs((y[i,k] <= z[k]  for k in vans for i in locations if i > 0), name='visitCustomer' )

# Travel time constraint
# Exclude the time to return to the depot

# travelTime = m.addConstrs((gp.quicksum(time[i,j]*x[i,j,k] for i,j in time.keys() if j > 0) == t[k] for k in vans), 
#                           name='travelTimeConstr' )

# Visit all customers
visitAll = m.addConstrs((y.sum(i,'*') == 1 for i in locations if i > 0), name='visitAll' )

# Depot constraint
depotConstr = m.addConstrs((y[0, k] == z[k] for k in vans), name='depotConstr' )

# Arriving at a customer location constraint
ArriveConstr = m.addConstrs((x.sum('*',j,k) == y[j,k] for j,k in y.keys()), name='ArriveConstr' )

# Leaving a customer location constraint
LeaveConstr = m.addConstrs((x.sum(j,'*',k) == y[j,k] for j,k in y.keys()), name='LeaveConstr' )

# breakSymm = m.addConstrs((y.sum('*',k-1) >= y.sum('*',k) for k in vans if k>0), name='breakSymm' )

demand_cons = m.addConstrs((gp.quicksum(y[j, k]*demands[j] 
                                          for j in locations[1:]) <= 15 for k in vans), 
                             name='demand_cons')

# Alternately, as a general constraint:
# maxTravelTime = m.addConstr(s == gp.max_(t), name='maxTravelTimeConstr')

m.ModelSense = GRB.MINIMIZE
m.setObjective(gp.quicksum(x[i, j, k]*time[i, j] 
                                for i, j in time.keys() 
                                for k in vans))

def get_subtours(sol):
    subtours = []
    LS = len(sol)
    unvisited = [K] + [1 for _ in range(N-1)]
    
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
        print(subtours)
        if len(subtours) > K:
            min_len = N
            for mini_tour in subtours[K:]:
                if len(mini_tour) < min_len:
                    tour = mini_tour
                    min_len = len(mini_tour)
            # tour = subtours[-1]
            print(tour)
            for k in vans:
                model.cbLazy(
                    gp.quicksum(
                        model._x[i, j, k] 
                        for i, j in permutations(tour, 2)) 
                    <= len(tour) - 1
                    )


# Verify model formulation

m.write('lost_luggage_distribution.lp')

# Run optimization engine
m._x = x
m.Params.LazyConstraints = 1
m.optimize(subtour_elim)

# Print optimal routes
for k in vans:
    route = [(i,j) for i,j in time.keys() if x[i,j,k].X > 0.5]
    print(route)
    # if route:
    #     i = 0
    #     print(f"Route for van {k}: {i}", end='')
    #     while True:
    #         i = route.select(i, '*')[0][1]
    #         print(f" -> {i}", end='')
    #         if i == 0:
    #             break
    #     print(f". Travel time: {round(t[k].X,2)} min")

# print(f"Max travel time: {round(s.X,2)}")

# make a list of edges selected in the solution
# vals = m.cbGetSolution(m._x)
selected = [(i,j) for i, j, k in m._x.keys() if x[i, j, k].X > 0.5]
print(selected)


"""
[(0, 0),
 (8, 36),
 (48, 4),
 (16, 7),
 (31, 48),
 (28, 30),
 (41, 24),
 (50, 13),
 (6, 31),
 (1, 24),
 (27, 38),
 (48, 49),
 (0, 44),
 (28, 17),
 (46, 14),
 (37, 6),
 (20, 1)]
"""

"""
Route for van 0: 0 -> 3 -> 16 -> 15 -> 2 -> 7 -> 14 -> 6 -> 5 -> 13 -> 0. Travel time: 105.42 min
Route for van 1: 0 -> 9 -> 8 -> 1 -> 12 -> 10 -> 4 -> 11 -> 0. Travel time: 104.78 min
Max travel time: 105.42
"""

"""
Optimal solution found (tolerance 1.00e-04)
Best objective 2.000000000000e+00, best bound 2.000000000000e+00, gap 0.0000%
"""

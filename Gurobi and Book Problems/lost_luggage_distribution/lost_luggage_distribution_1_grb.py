import sys
import math
import random
from itertools import permutations
import gurobipy as gp
from gurobipy import GRB

# number of locations, including the depot. The index of the depot is 0
n = 17
locations = [*range(n)]

# number of vans
K = 6
vans = [*range(K)]

# Create n random points
# Depot is located at (0,0) coordinates
random.seed(1)
points = [(0, 0)]
points += [(random.randint(0, 50), random.randint(0, 50)) for i in range(n-1)]


# Dictionary of Euclidean distance between each pair of points
# Assume a speed of 60 km/hr, which is 1 km/min. Hence travel time = distance
time = {(i, j):
        math.sqrt(sum((points[i][k]-points[j][k])**2 for k in range(2)))
        for i in locations for j in locations if i != j}
    
m = gp.Model('lost_luggage_distribution')

# Create variables: 

# x =1, if van  k  visits and goes directly from location  i  to location  j 
x = m.addVars(time.keys(), vans, vtype=GRB.BINARY, name='FromToBy')

# y = 1, if customer i is visited by van k
y = m.addVars(locations, vans, vtype=GRB.BINARY, name='visitBy')

# Number of vans used is a decision variable
z = m.addVars(vans, vtype=GRB.BINARY, name='used')

# Travel time per van
t = m.addVars(vans, ub=120, name='travelTime')

# Maximum travel time
s = m.addVar(name='maxTravelTime')

# Van utilization constraint

visitCustomer = m.addConstrs((y[i,k] <= z[k]  for k in vans for i in locations if i > 0), name='visitCustomer' )

# Travel time constraint
# Exclude the time to return to the depot

travelTime = m.addConstrs((gp.quicksum(time[i,j]*x[i,j,k] for i,j in time.keys() if j > 0) == t[k] for k in vans), 
                          name='travelTimeConstr' )

# Visit all customers
visitAll = m.addConstrs((y.sum(i,'*') == 1 for i in locations if i > 0), name='visitAll' )

# Depot constraint
depotConstr = m.addConstrs((y[0, k] == z[k] for k in vans), name='depotConstr' )

# Arriving at a customer location constraint
ArriveConstr = m.addConstrs((x.sum('*',j,k) == y[j,k] for j,k in y.keys()), name='ArriveConstr' )

# Leaving a customer location constraint
LeaveConstr = m.addConstrs((x.sum(j,'*',k) == y[j,k] for j,k in y.keys()), name='LeaveConstr' )

breakSymm = m.addConstrs((y.sum('*',k-1) >= y.sum('*',k) for k in vans if k>0), name='breakSymm' )

maxTravelTime = m.addConstrs((t[k] <= s for k in vans), name='maxTravelTimeConstr')

# Alternately, as a general constraint:
# maxTravelTime = m.addConstr(s == gp.max_(t), name='maxTravelTimeConstr')

m.ModelSense = GRB.MINIMIZE
m.setObjectiveN(z.sum(), 0, priority=1, name="Number of vans")
m.setObjectiveN(s, 1, priority=0, name="Travel time")

# Callback - use lazy constraints to eliminate sub-tours
def subtourelim(model, where):
    if where == GRB.Callback.MIPSOL:
        # make a list of edges selected in the solution
        vals = model.cbGetSolution(model._x)
        selected = gp.tuplelist((i,j) for i, j, k in model._x.keys()
                                if vals[i, j, k] > 0.5)
        # find the shortest cycle in the selected edge list
        tour = subtour(selected)
        if len(tour) < n: 
            for k in vans:
                model.cbLazy(gp.quicksum(model._x[i, j, k]
                                         for i, j in permutations(tour, 2))
                             <= len(tour)-1)


# Given a tuplelist of edges, find the shortest subtour not containing depot (0)
def subtour(edges):
    unvisited = list(range(1, n))
    cycle = range(n+1)  # initial length has 1 more city
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

# Verify model formulation

m.write('lost_luggage_distribution.lp')

# Run optimization engine
m._x = x
m.Params.LazyConstraints = 1
m.optimize(subtourelim)

# Print optimal routes
for k in vans:
    route = gp.tuplelist((i,j) for i,j in time.keys() if x[i,j,k].X > 0.5)
    if route:
        i = 0
        print(f"Route for van {k}: {i}", end='')
        while True:
            i = route.select(i, '*')[0][1]
            print(f" -> {i}", end='')
            if i == 0:
                break
        print(f". Travel time: {round(t[k].X,2)} min")

print(f"Max travel time: {round(s.X,2)}")


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
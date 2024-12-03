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

model.y = pyo.Var(model.N, model.V, within = pyo.Binary)
y = model.y

model.z = pyo.Var(model.V, within = pyo.Binary)
z = model.z

model.veh_time = pyo.Var(model.V, within = pyo.NonNegativeReals, bounds = (0, 120))
veh_time = model.veh_time

model.u = pyo.Var(model.N, model.V, within = pyo.NonNegativeReals)
u = model.u

# Constraints

"""
Van utilization: For all locations different from the depot, i.e.  i>0 , 
if the location is visited by van  k , then it is used.
"""

def van_uti(model, i, k):
    return y[i, k] <= z[k]
model.c1 = pyo.Constraint(model.C, model.V, rule = van_uti)

"""
Travel time: No van travels for more than 120 min. Note that we do not consider 
the travel time to return to the depot.
"""

# def travel_time(model, k):
#     return pyo.quicksum(x[i, j, k]*time[i, j] 
#                         for i in model.N 
#                         for j in model.C if i != j) <= 120
# model.c2 = pyo.Constraint(model.V, rule = travel_time)

def travel_time(model, k):
    return pyo.quicksum(x[i, j, k]*time[i, j] 
                        for i, j in time.keys() if j > 1) <= 120
model.c2 = pyo.Constraint(model.V, rule = travel_time)

"""
Visit all customers: Each customer location is visited by exactly one van.
"""

def once(model, i):
    return pyo.quicksum(y[i, k] for k in model.V) == 1
model.c3 = pyo.Constraint(model.C, rule = once)

"""
Depot: Heathrow is visited by every van used. (Note: to improve performance, 
we diverge from the book by disaggregating this constraint).
"""

def depot(model, k):
    return y[1, k] == z[k]
model.c4 = pyo.Constraint(model.V, rule = depot)

"""
Arriving at a location: If location j is visited by van k , 
then the van is coming from another location i.
"""

def arrival(model, j, k):
    return (pyo.quicksum(x[i, j, k] 
                         for i in model.N if i != j)) == y[j, k]
model.c5 = pyo.Constraint(model.N, model.V, rule = arrival)

"""
Leaving a location: If van k leaves location j , 
then the van is going to another location i.
"""

def departure(model, j, k):
    return (pyo.quicksum(x[j, i, k] 
                         for i in model.N if i != j)) == y[j, k]
model.c6 = pyo.Constraint(model.N, model.V, rule = departure)

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
    return pyo.quicksum(z[k] for k in model.V)
model.obj = pyo.Objective(rule = obj_fn, sense = pyo.minimize)

# Solution

sol = SolverFactory("cplex")
sol.options["timelimit"] = 10
res = sol.solve(model)

# Printing the Solution

print(res)

vehi_dict = {v : [] for v in model.V}
vehi_dist = {v : 0 for v in model.V}

for k in model.V:
    for i in model.N:
        for j in model.N:
            if x[i, j, k]() and x[i, j, k]() >= 0.9:
                print(f"x[{i}, {j}, {k}] = {x[i, j, k]()}")
                vehi_dict[k].append((i, j))
    print(f"veh_time[{k}] = {veh_time[k]()}")

for v in vehi_dict:
    if vehi_dict[v]:
        for i, j in vehi_dict[v]:
            vehi_dist[v] += time[i, j]


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









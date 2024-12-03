import pyomo.environ as pyo
from pyomo.opt import SolverFactory

model = pyo.ConcreteModel()

N = 15

distances = [ [0, 2448, 791, 1420, 2136, 94, 1634, 2451, 1373, 2573, 1783, 890, 1371, 532, 634], [2448, 0, 1745, 1375, 371, 2340, 1185, 164, 1436, 344, 1320, 2448, 1383, 1906, 2274], [791, 1745, 0, 937, 1743, 787, 1019, 1682, 959, 1842, 1090, 1028, 802, 357, 557], [1420, 1375, 937, 0, 1130, 1506, 197, 1184, 239, 1613, 165, 1156, 358, 1189, 1338], [2136, 371, 1743, 1130, 0, 2034, 893, 355, 1160, 358, 1399, 2136, 1486, 1705, 2057], [94, 2340, 787, 1506, 2034, 0, 1561, 2361, 1320, 2530, 1717, 983, 1437, 629, 604], [1634, 1185, 1019, 197, 893, 1561, 0, 1177, 433, 1573, 360, 1437, 151, 1029, 1449], [2451, 164, 1682, 1184, 355, 2361, 1177, 0, 1606, 250, 1312, 2451, 1458, 1910, 2283], [1373, 1436, 959, 239, 1160, 1320, 433, 1606, 0, 1464, 330, 1166, 479, 1052, 1270], [2573, 344, 1842, 1613, 358, 2530, 1573, 250, 1464, 0, 1474, 2573, 1690, 1956, 2347], [1783, 1320, 1090, 165, 1399, 1717, 360, 1312, 330, 1474, 0, 1783, 1138, 1236, 1513], [890, 2448, 1028, 1156, 2136, 983, 1437, 2451, 1166, 2573, 1138, 0, 1305, 867, 897], [1371, 1383, 802, 358, 1486, 1437, 151, 1458, 479, 1690, 1236, 1305, 0, 880, 1084], [532, 1906, 357, 1189, 1705, 629, 1029, 1910, 1052, 1956, 1513, 867, 880, 0, 638], [634, 2274, 557, 1338, 2057, 604, 1449, 2283, 1270, 2347, 1513, 897, 1084, 638, 0] ]

# Sets and Parameters

model.cities = pyo.RangeSet(1, N)

model.distance_network = pyo.Param(model.cities, model.cities, within = pyo.Any, 
                                   initialize = {
                                       (i, j) : distances[i-1][j-1] 
                                       for i in model.cities 
                                       for j in model.cities
                                       })
distance_network = model.distance_network

# Variables

model.x = pyo.Var(model.cities, model.cities, within = pyo.Binary)
x = model.x

model.u = pyo.Var(model.cities, within = pyo.NonNegativeReals)
u = model.u

# Constraints

def row_once(model, j):
    return sum(x[i, j] for i in model.cities if i != j) == 1
model.c1 = pyo.Constraint(model.cities, rule = row_once)

def col_once(model, i):
    return sum(x[i, j] for j in model.cities if i != j) == 1
model.c2 = pyo.Constraint(model.cities, rule = col_once)

model.sub_tour = pyo.ConstraintList()

for i in model.cities:
    for j in model.cities:
        if i != j and i != 1:
            model.sub_tour.add(
                u[i] - u[j] + N*(x[i, j]) <= N-1
                )

# Objective Function

def obj_fn(model):
    return sum(x[i, j]*distance_network[i, j] 
               for i in model.cities 
               for j in model.cities if i != j)
model.obj = pyo.Objective(rule = obj_fn, sense = pyo.minimize)

# Solution

sol = SolverFactory("cplex")
res = sol.solve(model)

# Printing the Results

tour = []
tour_dict = {}

for i in model.cities:
    for j in model.cities:
        if x[i, j]() and x[i, j]() >= 0.9:
            tour.append((i, j))
            tour_dict[i] = j

sys_tour = [1]

print("Tour Path : ")

while len(sys_tour) < len(tour):
    last = tour_dict[sys_tour[-1]]
    sys_tour.append(last)
    
for city in sys_tour:
    if city == 1:
        print(f"{city}", end = " ")
    elif city == sys_tour[-1]:
        print(f"--> {city} --> 1")
    else:
        print(f"--> {city}", end = " ")

print(f"\nTotal Distance Travelled by Salesman : {model.obj()} km.")








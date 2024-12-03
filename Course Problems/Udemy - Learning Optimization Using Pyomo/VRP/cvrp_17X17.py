import pyomo.environ as pyo, time
from pyomo.opt import SolverFactory

start = time.time()

model = pyo.ConcreteModel()

NC = 17
NV = 4

demands_list = [0, 1, 1, 2, 4, 2, 4, 8, 8, 1, 2, 1, 2, 4, 4, 8, 8]
vehicle_capacities = [15, 15, 15, 15]

distance_matrix = [
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

# Sets and Parameters

model.N = pyo.RangeSet(1, NC)
model.C = pyo.RangeSet(2, NC)
model.V = pyo.RangeSet(1, NV)

model.capacities = pyo.Param(model.V, within = pyo.Any, 
                             initialize = {
                                 v : vehicle_capacities[v-1] 
                                 for v in model.V
                                 })
capacities = model.capacities

model.demands = pyo.Param(model.N, within = pyo.Any, 
                             initialize = {
                                 c : demands_list[c-1] 
                                 for c in model.N
                                 })
demands = model.demands

model.distances = pyo.Param(model.N, model.N, within = pyo.Any, 
                            initialize = {
                                (c1, c2) : distance_matrix[c1-1][c2-1] 
                                for c1 in model.N 
                                for c2 in model.N
                                })
distances_network = model.distances

# Variables

model.x = pyo.Var(model.N, model.N, model.V, within = pyo.Binary)
x = model.x

model.u = pyo.Var(model.N, model.V, within = pyo.NonNegativeReals)
u = model.u

# Constraints

def route_once(model, j):
    return sum(x[i, j, k] for i in model.N 
               for k in model.V if i != j) == 1
model.c1 = pyo.Constraint(model.C, rule = route_once)

def initial_flow(model, k):
    return sum(x[1, j, k] for j in model.C) == 1
model.c2 = pyo.Constraint(model.V, rule = initial_flow)

def maintain_flow(model, j, k):
    return sum(x[i, j, k] for i in model.N if i != j) == sum(x[j, i, k] for i in model.N if i != j)
model.c3 = pyo.Constraint(model.C, model.V, rule = maintain_flow)

def demand_cons(model, k):
    return sum(x[i, j, k]*demands[j] 
               for i in model.N 
               for j in model.C if i != j) <= capacities[k]
model.c4 = pyo.Constraint(model.V, rule = demand_cons)

model.sub_tour = pyo.ConstraintList()

for i in model.C:
    for j in model.C:
        for k in model.V:
            if i != j:
                model.sub_tour.add(
                    u[i, k] - u[j, k] + NC*(x[i, j, k]) <= NC-1
                    )

# Objective Function

def obj_fn(model):
    return sum(x[i, j, k]*distances_network[i, j] 
               for i in model.N 
               for j in model.N 
               for k in model.V if i != j)
model.obj = pyo.Objective(rule = obj_fn)

# Solution

sol = SolverFactory("cplex")
sol.options["timelimit"] = 10
res = sol.solve(model, tee = True)

# Printing the Results

vehicle_dict = {v : [] for v in model.V}

loads = {v : 0 for v in model.V}

distance_by_vehicle = {v : 0 for v in model.V}

for i in model.N:
    for j in model.N:
        for k in model.V:
            if x[i, j, k]() and x[i, j, k]() >= 0.9:
                vehicle_dict[k].append((i, j))
                loads[k] += demands[j]
                distance_by_vehicle[k] += distances_network[i, j]

print(f"Total Distance Travelled by all Vehicles : {model.obj()} m.")
        
print(f"Total Time taken by Solver : {round(time.time() - start, 4)} sec.")







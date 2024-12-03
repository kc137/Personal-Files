import pyomo.environ as pyo, pandas as pd
from pyomo.opt import SolverFactory
from collections import defaultdict

NC = 17
NV = 4
M = 1000

# Model

model = pyo.ConcreteModel()

# Sets and Parameters

model.N = pyo.Set(initialize = ["C" + str(i) for i in range(1, NC + 1)])
model.V = pyo.Set(initialize = ["V" + str(i) for i in range(1, NV + 1)])
model.C = pyo.Set(initialize = ["C" + str(i) for i in range(2, NC + 1)])

disdata = [
        [
            0, 548, 776, 696, 582, 274, 502, 194, 308, 194, 536, 502, 388, 354,
            468, 776, 662
        ],
        [
            548, 0, 684, 308, 194, 502, 730, 354, 696, 742, 1084, 594, 480, 674,
            1016, 868, 1210
        ],
        [
            776, 684, 0, 992, 878, 502, 274, 810, 468, 742, 400, 1278, 1164,
            1130, 788, 1552, 754
        ],
        [
            696, 308, 992, 0, 114, 650, 878, 502, 844, 890, 1232, 514, 628, 822,
            1164, 560, 1358
        ],
        [
            582, 194, 878, 114, 0, 536, 764, 388, 730, 776, 1118, 400, 514, 708,
            1050, 674, 1244
        ],
        [
            274, 502, 502, 650, 536, 0, 228, 308, 194, 240, 582, 776, 662, 628,
            514, 1050, 708
        ],
        [
            502, 730, 274, 878, 764, 228, 0, 536, 194, 468, 354, 1004, 890, 856,
            514, 1278, 480
        ],
        [
            194, 354, 810, 502, 388, 308, 536, 0, 342, 388, 730, 468, 354, 320,
            662, 742, 856
        ],
        [
            308, 696, 468, 844, 730, 194, 194, 342, 0, 274, 388, 810, 696, 662,
            320, 1084, 514
        ],
        [
            194, 742, 742, 890, 776, 240, 468, 388, 274, 0, 342, 536, 422, 388,
            274, 810, 468
        ],
        [
            536, 1084, 400, 1232, 1118, 582, 354, 730, 388, 342, 0, 878, 764,
            730, 388, 1152, 354
        ],
        [
            502, 594, 1278, 514, 400, 776, 1004, 468, 810, 536, 878, 0, 114,
            308, 650, 274, 844
        ],
        [
            388, 480, 1164, 628, 514, 662, 890, 354, 696, 422, 764, 114, 0, 194,
            536, 388, 730
        ],
        [
            354, 674, 1130, 822, 708, 628, 856, 320, 662, 388, 730, 308, 194, 0,
            342, 422, 536
        ],
        [
            468, 1016, 788, 1164, 1050, 514, 514, 662, 320, 274, 388, 650, 536,
            342, 0, 764, 194
        ],
        [
            776, 868, 1552, 560, 674, 1050, 1278, 742, 1084, 810, 1152, 274,
            388, 422, 764, 0, 798
        ],
        [
            662, 1210, 754, 1358, 1244, 708, 480, 856, 514, 468, 354, 844, 730,
            536, 194, 798, 0
        ],
    ]

disdatapd = pd.DataFrame(disdata, index = model.N, columns = model.N)
distance = disdatapd

model.pick_deli = pyo.Param(domain = pyo.Any, initialize = [
        ["C2", "C7"],
        ["C3", "C11"],
        ["C5", "C4"],
        ["C6", "C10"],
        ["C8", "C9"],
        ["C16", "C12"],
        ["C14", "C13"],
        ["C17", "C15"],
    ])

cus_demand = [0] + [1 for i in range(NC - 1)]
dem_dict = {}
for i in range(NC):
    dem_dict[model.N[i+1]] = cus_demand[i]

model.demand = pyo.Param(model.N, initialize = dem_dict)

dist_dict = defaultdict(int)

for Ve in model.V:
    dist_dict[Ve] = 0

# Variables

model.x = pyo.Var(model.N, model.N, model.V, domain = pyo.Binary)
x = model.x
model.u = pyo.Var(model.N, domain = pyo.NonNegativeReals)
u = model.u
model.cumu_dist = pyo.Var(model.N, model.V, domain = pyo.NonNegativeReals)
cumu_dist = model.cumu_dist
model.bin_veh = pyo.Var(model.N, model.V, domain = pyo.Binary)
bin_veh = model.bin_veh

# Constraints

# def route_len(model, k):
#     return sum(model.x[i, j, k]*model.demand[i] 
#                 for i in model.N 
#                 for j in model.C if j != i) <= NV
# model.routel_constraint = pyo.Constraint(model.V, rule=route_len)

model.max_dist_cons = pyo.ConstraintList()
for k in model.V:
    model.max_dist_cons.add(sum(x[i, j, k]*distance[j][i] for i in model.N for j in model.N) <= 2200)
    model.max_dist_cons.add(sum(x[i, j, k]*distance[j][i] for i in model.N for j in model.N) >= 1000)

def Enter(model, j, k):
    return (sum(x[i, j, k] for i in model.N if i != j) == 
            sum(x[j, i, k] for i in model.N))
model.enter = pyo.Constraint(model.N, model.V, rule = Enter)

def flow_rule(model, j):
    return sum(x[i, j, k] for i in model.N 
               for k in model.V if i != j) == 1
model.flow__rule = pyo.Constraint(model.C, rule = flow_rule)

model.depot = pyo.ConstraintList()
for k in model.V:
    model.depot.add(sum(x["C1", j, k] for j in model.C) == 1)
    model.depot.add(sum(x[i, "C1", k] for i in model.C) == 1)

def Subtour(model, i, j, k):
    if i != j:
        return u[i] - u[j] + (NC - 1)*x[i, j, k] <= (NC - 2)
    else:
        return u[j] == u[j]
model.sub_tour = pyo.Constraint(model.C, model.C, model.V, rule = Subtour)

# Objective Function

def Obj_Fn(model):
    return sum(x[i, j, k]*distance[j][i] if i != j else 0 
               for k in model.V
               for i in model.N
               for j in model.N)
model.Obj = pyo.Objective(rule = Obj_Fn, sense = pyo.minimize)

model.dist_cons = pyo.ConstraintList()

model.pick_deli_cons = pyo.ConstraintList()
# model.pick_deli_cons.add(sum(bin_veh[k] for k in model.V) == 1)
for k in model.V:
    for pack in model.pick_deli():
        model.pick_deli_cons.add(sum(x[i, pack[0], k] for i in model.N) == bin_veh[pack[0], k])
        model.pick_deli_cons.add(sum(x[i, pack[1], k] for i in model.N) == bin_veh[pack[1], k])

for pack in model.pick_deli():
    model.pick_deli_cons.add(sum(bin_veh[pack[0], k] for k in model.V) == 1)
    model.dist_cons.add(u[pack[0]] <= u[pack[1]] + 0.00001)
    for k in model.V:
        model.pick_deli_cons.add(bin_veh[pack[0], k] == bin_veh[pack[1], k])

# Solution

sol = SolverFactory("cplex")
res = sol.solve(model)

# Printing the Solution

for k in model.V:
    route = []
    print(f'Route for Vehicle-{k}:\n')
    for i in model.N:
        for j in model.N:
            if x[i, j, k]() and x[i, j, k]() > 0.9:
                dist_dict[k] += distance[j][i]
                # route.append((f"{i}--{j}"))
                route.append((i, j))
    print(route)
    print(f"\nVehicle-{k} travelled {dist_dict[k]} m.\n")
print(f"Total Distance Travelled by all {NV}-Vehicles = {sum(dist_dict.values())} m")



















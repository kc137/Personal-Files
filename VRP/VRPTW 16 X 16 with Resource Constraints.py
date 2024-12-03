import pyomo.environ as pyo, pandas as pd
from collections import defaultdict
from pyomo.opt import SolverFactory

model = pyo.ConcreteModel()

N = 17
V = 4
M = 1000

# Sets and Parameters

model.CUSTOMERS = pyo.Set(initialize = ["D"] + ["A" + str(c) for c in range(1, N)])
model.customers = pyo.Set(initialize = ["A" + str(c) for c in range(1, N)])
model.VEHICLES = pyo.Set(initialize = ["V" + str(v) for v in range(1, V+1)])

demdata = [[0, 6, 9, 8, 7, 3, 6, 2, 3, 2, 6, 6, 4, 4, 5, 9, 7], 
            [6, 0, 8, 3, 2, 6, 8, 4, 8, 8, 13, 7, 5, 8, 12, 10, 14], 
            [9, 8, 0, 11, 10, 6, 3, 9, 5, 8, 4, 15, 14, 13, 9, 18, 9], 
            [8, 3, 11, 0, 1, 7, 10, 6, 10, 10, 14, 6, 7, 9, 14, 6, 16], 
            [7, 2, 10, 1, 0, 6, 9, 4, 8, 9, 13, 4, 6, 8, 12, 8, 14], 
            [3, 6, 6, 7, 6, 0, 2, 3, 2, 2, 7, 9, 7, 7, 6, 12, 8], 
            [6, 8, 3, 10, 9, 2, 0, 6, 2, 5, 4, 12, 10, 10, 6, 15, 5], 
            [2, 4, 9, 6, 4, 3, 6, 0, 4, 4, 8, 5, 4, 3, 7, 8, 10], 
            [3, 8, 5, 10, 8, 2, 2, 4, 0, 3, 4, 9, 8, 7, 3, 13, 6], 
            [2, 8, 8, 10, 9, 2, 5, 4, 3, 0, 4, 6, 5, 4, 3, 9, 5], 
            [6, 13, 4, 14, 13, 7, 4, 8, 4, 4, 0, 10, 9, 8, 4, 13, 4], 
            [6, 7, 15, 6, 4, 9, 12, 5, 9, 6, 10, 0, 1, 3, 7, 3, 10], 
            [4, 5, 14, 7, 6, 7, 10, 4, 8, 5, 9, 1, 0, 2, 6, 4, 8], 
            [4, 8, 13, 9, 8, 7, 10, 3, 7, 4, 8, 3, 2, 0, 4, 5, 6], 
            [5, 12, 9, 14, 12, 6, 6, 7, 3, 3, 4, 7, 6, 4, 0, 9, 2], 
            [9, 10, 18, 6, 8, 12, 15, 8, 13, 9, 13, 3, 4, 5, 9, 0, 9], 
            [7, 14, 9, 16, 14, 8, 5, 10, 6, 5, 4, 10, 8, 6, 2, 9, 0]]

times = pd.DataFrame(demdata, index = model.CUSTOMERS, columns = model.CUSTOMERS)

datatw = [
        (0, 5),  # depot
        (7, 12),  # 1
        (10, 15),  # 2
        (5, 14),  # 3
        (5, 13),  # 4
        (0, 5),  # 5
        (5, 10),  # 6
        (0, 10),  # 7
        (5, 10),  # 8
        (0, 5),  # 9
        (10, 16),  # 10
        (10, 15),  # 11
        (0, 5),  # 12
        (5, 10),  # 13
        (7, 12),  # 14
        (10, 15),  # 15
        (5, 15),  # 16
    ]

tw_dict = {}

for i in range(len(datatw)):
    tw_dict[model.CUSTOMERS[i+1]] = datatw[i]

model.time_window = pyo.Param(model.CUSTOMERS, domain = pyo.Any, initialize = tw_dict)

time = defaultdict(int)

for V in model.VEHICLES:
    time[V] = 0

start_times = [0, 5, 5, 0]
vehicle_start = {}
for ix in range(len(model.VEHICLES)):
    vehicle_start[model.VEHICLES[ix+1]] = start_times[ix]

model.start = pyo.Param(model.VEHICLES, initialize = vehicle_start)

# Variables

# Binary Decision Variable
model.x = pyo.Var(model.CUSTOMERS, model.CUSTOMERS, model.VEHICLES, domain = pyo.Binary)
x = model.x
# Service Times
model.s = pyo.Var(model.CUSTOMERS, model.VEHICLES, domain = pyo.NonNegativeReals)
s = model.s
# Times including vehicle starting times
model.t = pyo.Var(model.CUSTOMERS, model.VEHICLES, domain = pyo.NonNegativeReals)
t = model.t

# Constraints

def once(model, i):
    return sum(x[i, j, k] for j in model.CUSTOMERS
               for k in model.VEHICLES) == 1
model.path_once = pyo.Constraint(model.customers, rule = once)

model.enter = pyo.ConstraintList()

for k in model.VEHICLES:
    for j in model.customers:    
        model.enter.add(sum(x[i, j, k] for i in model.CUSTOMERS if i != j) == 
                        sum(x[j, i, k] for i in model.CUSTOMERS))

def depot1(model, k):
    return sum(x["D", j, k] for j in model.customers) == 1
model.depot_to_customer = pyo.Constraint(model.VEHICLES, rule = depot1)

def depot2(model, k):
    return sum(x[i, "D", k] for i in model.customers) == 1
model.customer_to_depot = pyo.Constraint(model.VEHICLES, rule = depot2)

def serve(model, i, j, k):
    if i != j:
        return s[i, k] + times[j][i] - M*(1 - x[i, j, k]) <= s[j, k] - 0.00001
    else:
        return s[i, k] == s[i, k]
model.service_time = pyo.Constraint(model.CUSTOMERS, model.customers, model.VEHICLES, rule = serve)

model.service_times_add = pyo.ConstraintList()

def service_window1(model, k, i):
    return model.time_window[i][0] <= s[i, k]
model.window_cons1 = pyo.Constraint(model.VEHICLES, model.customers, rule = service_window1)

def service_window2(model, k, i):
    return model.time_window[i][1] >= s[i, k] - 0.001
model.window_cons2 = pyo.Constraint(model.VEHICLES, model.customers, rule = service_window2)

model.vehicle_start_time = pyo.ConstraintList()
for k in model.VEHICLES:
    model.vehicle_start_time.add(s["D", k] == model.start[k])



# Objective Function

def Obj_Fn(model):
    return sum(x[i, j, k]*times[j][i] for i in model.CUSTOMERS
               for j in model.CUSTOMERS for k in model.VEHICLES if i != j)
model.Obj = pyo.Objective(rule = Obj_Fn, sense = pyo.minimize)

# Solution

sol = SolverFactory("cplex")
res = sol.solve(model)

print(f"\nObjective Function = {model.Obj()}\n")
total_load = 0
routes = defaultdict(list)
for k in model.VEHICLES:
    tload = 0
    print(f'Route for vehicle-{k}:')
    route = [f"{(i, j)} : ({times[j][i]})" for i in model.CUSTOMERS
              for j in model.CUSTOMERS
              if (model.x[i, j, k]() and model.x[i, j, k]() >= 0.9)]
    for i in model.CUSTOMERS:
        for j in model.CUSTOMERS:
            if model.x[i, j, k]() and model.x[i, j, k]() >= 0.9:
                routes[k].append((i, j))
                time[k] += times[j][i]
                # tload += model.demand[j]
    # total_load += tload
    print(route)    
















import pyomo.environ as pyo, pandas as pd
from collections import defaultdict
from pyomo.opt import SolverFactory

model = pyo.ConcreteModel()

# Sets and Parameters

model.CUSTOMERS = pyo.Set(initialize = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q'])
model.cust = pyo.Set(initialize = ['B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q'])
model.VEHICLES = pyo.Set(initialize = ['V1', 'V2', 'V3', 'V4'])
M = 10e2

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



# [[1000.0, 6, 9, 8, 7, 3, 6, 2, 3, 2, 6],
#  [6, 1000.0, 8, 3, 2, 6, 8, 4, 8, 8, 13],
#  [9, 8, 1000.0, 11, 10, 6, 3, 9, 5, 8, 4],
#  [8, 3, 11, 1000.0, 1, 7, 10, 6, 10, 10, 14],
#  [7, 2, 10, 1, 1000.0, 6, 9, 4, 8, 9, 13],
#  [3, 6, 6, 7, 6, 1000.0, 2, 3, 2, 2, 7],
#  [6, 8, 3, 10, 9, 2, 1000.0, 6, 2, 5, 4],
#  [2, 4, 9, 6, 4, 3, 6, 1000.0, 4, 4, 8],
#  [3, 8, 5, 10, 8, 2, 2, 4, 1000.0, 3, 4],
#  [2, 8, 8, 10, 9, 2, 5, 4, 3, 1000.0, 4],
#  [6, 13, 4, 14, 13, 7, 4, 8, 4, 4, 1000.0]]

demdatapd = pd.DataFrame(demdata, index = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O'], columns = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O'])

model.time_window = pyo.Param(model.CUSTOMERS, domain = pyo.Any, initialize = {
    'A': (0, 5), 'B': (7, 12), 'C': (10, 15), 'D': (16, 18), 
    'E': (10, 13), 'F': (0, 5), 'G': (5, 10), 'H' : (0, 4), 
    'I' : (5, 10), 'J' : (0, 3), 'K' : (10, 16), 'L' : (10, 15), 
    'M' : (0, 5), 'N' : (5, 10), 'O' : (7, 8)})

time = defaultdict(int)

for V in model.VEHICLES:
    time[V] = 0

model.times = demdatapd
times = model.times

# Variables

model.x = pyo.Var(model.CUSTOMERS, model.CUSTOMERS, model.VEHICLES, domain = pyo.Binary)
x = model.x
model.s = pyo.Var(model.CUSTOMERS, model.VEHICLES, domain = pyo.NonNegativeReals)
s = model.s

# Constraints

# def capacity(model, k):
#     return sum(model.x[i, j, k]*model.demand[j] if i != j else 0
#                 for i in model.CUSTOMERS 
#                 for j in model.cust if j != i) <= model.capacity[k]
# model.capacity_constraint = pyo.Constraint(model.VEHICLES, rule=capacity)

model.enter = pyo.ConstraintList()

for j in model.cust:
    for k in model.VEHICLES:
        model.enter.add(sum(x[i, j, k] for i in model.CUSTOMERS if i != j) == 
                        sum(x[j, i, k] for i in model.CUSTOMERS))

model.flow_rule = pyo.ConstraintList()

def flow_rule(model, i):
    return sum(x[i, j, k]
               for j in model.CUSTOMERS
               for k in model.VEHICLES) == 1
model.flow_constraint = pyo.Constraint(model.cust, rule=flow_rule)

def depot(model, k):
    return sum(x["A", j, k] for j in model.cust) == 1
model.depot_cons = pyo.Constraint(model.VEHICLES, rule = depot)

def depot2(model, k):
    return sum(x[i, "A", k] for i in model.cust) == 1
model.depot_cons2 = pyo.Constraint(model.VEHICLES, rule = depot2)

def service(model, i, j, k):
    if i != j:
        return (s[i, k] + times[j][i] - M*(1 - x[i, j, k]) <= s[j, k])
    else:
        return s[i, k] == s[i, k]
model.service_time = pyo.Constraint(model.cust, model.cust, model.VEHICLES, rule = service)

def service_window1(model, i, k):
    return model.time_window[i][0] <= s[i, k]
model.service_cons2 = pyo.Constraint(model.CUSTOMERS, model.VEHICLES, rule = service_window1)

def service_window2(model, i, k):
    return model.time_window[i][1] >= s[i, k]
model.service_cons3 = pyo.Constraint(model.CUSTOMERS, model.VEHICLES, rule = service_window2)

# Objective Function

def Obj_Fn(model):
    return sum(x[i, j, k]*times[j][i] for i in model.CUSTOMERS for j in model.CUSTOMERS
               for k in model.VEHICLES if i != j)
model.Obj = pyo.Objective(rule = Obj_Fn, sense = pyo.minimize)

# Solution

sol = SolverFactory("cplex")
res = sol.solve(model)

print(f"Objective Function = {model.Obj()}")
# total_load = 0
total_time = 0
for k in model.VEHICLES:
    # tload = 0
    timeroute = 0
    print(f'Route for vehicle-{k}:')
    route = [f"{(i, j)}->{model.time_window[j]}, {s[i, k]()}, {s[j, k]()}, {times[j][i]}" for i in model.CUSTOMERS
              for j in model.CUSTOMERS
              if (model.x[i, j, k].value == 1)]
    for i in model.CUSTOMERS:
        for j in model.CUSTOMERS:
            if model.x[i, j, k]() == 1:
                time[k] += model.times[j][i]
                if s[i, k]() + times[j][i] > timeroute:
                    timeroute = s[i, k]() + times[j][i]
                # tload += model.demand[j]
    # total_load += tload
    total_time += timeroute
    print(route)
    print(f"Total time taken by {k} = {timeroute}.")
    # print(f"\nVehicle-{k} travelled {dist[k]} m with a total load of {tload} tons\n")
# print(f"Total load after all routes = {total_load} tons")
print(f"\nTotal time taken by all vehicles = {total_time} hours.\n")

# for k in model.VEHICLES:
#     for i in model.CUSTOMERS:
#         for j in model.CUSTOMERS:
#             if model.x[i, j, k]():
#                 print(f"{model.x[i, j, k]} = {model.x[i, j, k]()}")












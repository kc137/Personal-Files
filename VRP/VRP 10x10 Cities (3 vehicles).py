# Import Pyomo library and Solver
import numpy as np
np.float_ = np.float64

import pyomo.environ as pyo
from pyomo.opt import SolverFactory
from collections import defaultdict

import pandas as pd

# Model
model = pyo.ConcreteModel()

# Sets
model.CUSTOMERS = pyo.Set(initialize = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K'])
model.cust = pyo.Set(initialize = ['B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K'])
model.VEHICLES = pyo.Set(initialize = ['V1', 'V2', 'V3'])

# Parameters
# demdata = [
#     [
#         10000, 548, 776, 696, 582, 274, 502, 194, 308, 194, 536],
#     [
#         548, 10000, 684, 308, 194, 502, 730, 354, 696, 742, 1084],
#     [
#         776, 684, 10000, 992, 878, 502, 274, 810, 468, 742, 400],
#     [
#         696, 308, 992,10000, 114, 650, 878, 502, 844, 890, 1232],
#     [
#         582, 194, 878, 114, 10000, 536, 764, 388, 730, 776, 1118],
#     [
#         274, 502, 502, 650, 536, 10000, 228, 308, 194, 240, 582],
#     [
#         502, 730, 274, 878, 764, 228, 10000, 536, 194, 468, 354],
#     [
#         194, 354, 810, 502, 388, 308, 536, 10000, 342, 388, 730],
#     [
#         308, 696, 468, 844, 730, 194, 194, 342, 10000, 274, 388],
#     [
#         194, 742, 742, 890, 776, 240, 468, 388, 274, 10000, 342], 
#     [
#         536, 1084, 400, 1232, 1118, 582, 354, 730, 388, 342, 10000]
# ]

demdata = [[
        0, 548, 776, 696, 582, 274, 502, 194, 308, 194, 536],
    [
        548, 0, 684, 308, 194, 502, 730, 354, 696, 742, 1084],
    [
        776, 684, 0, 992, 878, 502, 274, 810, 468, 742, 400],
    [
        696, 308, 992, 0, 114, 650, 878, 502, 844, 890, 1232],
    [
        582, 194, 878, 114, 0, 536, 764, 388, 730, 776, 1118],
    [
        274, 502, 502, 650, 536, 0, 228, 308, 194, 240, 582],
    [
        502, 730, 274, 878, 764, 228, 0, 536, 194, 468, 354],
    [
        194, 354, 810, 502, 388, 308, 536, 0, 342, 388, 730],
    [
        308, 696, 468, 844, 730, 194, 194, 342, 0, 274, 388],
    [
        194, 742, 742, 890, 776, 240, 468, 388, 274, 0, 342], 
    [
        536, 1084, 400, 1232, 1118, 582, 354, 730, 388, 342, 0]
]

demdatapd = pd.DataFrame(demdata, index = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K'], columns = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K'])

# demand = pd.read_excel("VRP RP1.xlsx", header = 9, usecols = "A:H", nrows = 2)
model.demand = pyo.Param(model.CUSTOMERS, initialize = {
    'A': 0, 'B': 1, 'C': 1, 'D': 2, 
    'E': 4, 'F': 2, 'G': 4, 'H' : 8, 
    'I' : 8, 'J' : 1, 'K' : 2})
model.capacity = pyo.Param(model.VEHICLES, initialize = {'V1': 15, 'V2': 15, 'V3' : 15})

dist = defaultdict(int)

for V in model.VEHICLES:
    dist[V] = 0

model.distance = demdatapd

# Variables
model.x = pyo.Var(model.CUSTOMERS, model.CUSTOMERS, model.VEHICLES, within=pyo.Binary)
model.u = pyo.Var(model.cust, within=pyo.NonNegativeReals)

# Objective function
def objective_rule(model):
    return sum(model.distance[j][i] * model.x[i, j, k] if j != i else 0
               for i in model.CUSTOMERS
               for j in model.CUSTOMERS
                for k in model.VEHICLES)
model.objective = pyo.Objective(rule=objective_rule, sense = pyo.minimize)

# Constraints

def capacity(model, k):
    return sum(model.x[i, j, k]*model.demand[j] if i != j else 0
                for i in model.CUSTOMERS 
                for j in model.cust if j != i) <= model.capacity[k]
model.capacity_constraint = pyo.Constraint(model.VEHICLES, rule=capacity)

def enter(model, j, k):
    return sum(model.x[i, j, k] for i in model.CUSTOMERS if i != j) == (
        (sum(model.x[j, i, k] for i in model.CUSTOMERS)))
model.enter_go = pyo.Constraint(model.CUSTOMERS, model.VEHICLES, rule=enter)

def flow_rule(model, j):
    return sum(model.x[i, j, k]
               for i in model.CUSTOMERS
               for k in model.VEHICLES) == 1
model.flow_constraint = pyo.Constraint(model.cust, rule=flow_rule)

model.depot = pyo.ConstraintList()
for k in model.VEHICLES:
    model.depot.add(sum(model.x["A", j, k] for j in model.cust) == 1)
    # model.depot.add(sum(model.x[i, "A", k] for i in model.cust) == 1)

def subtour(model, i, j, k):
    if i != j:
        return model.u[i] - model.u[j] >= model.demand[j] - model.capacity[k]*(1 - model.x[i, j, k])
    else:
        return model.u[i] - model.u[i] == 0
model.sub_tour = pyo.Constraint(model.cust, model.cust, model.VEHICLES, rule = subtour)

model.subtour = pyo.ConstraintList()
for i in model.cust:
    for k in model.VEHICLES:
        model.subtour.add(model.demand[i] <= model.u[i])
        model.subtour.add(model.capacity[k] >= model.u[i])



# Solution
solver = SolverFactory('cplex')
results = solver.solve(model)

# Print the results
print('Objective value:', model.objective())
total_load = 0
for k in model.VEHICLES:
    tload = 0
    print(f'Route for vehicle-{k}:')
    route = [f"{(i, j)} -> {model.demand[j]}" for i in model.CUSTOMERS
              for j in model.CUSTOMERS
              if (model.x[i, j, k].value == 1) if i != j]
    for i in model.CUSTOMERS:
        for j in model.CUSTOMERS:
            if model.x[i, j, k]() == 1:
                dist[k] += model.distance[j][i]
                tload += model.demand[j]
    total_load += tload
    print(route)
    print(f"\nVehicle-{k} travelled {dist[k]} m with a total load of {tload} tons\n")
print(f"Total load after all routes = {total_load} tons")

# for i in model.CUSTOMERS:
#     for j in model.CUSTOMERS:
#         for k in model.VEHICLES:
#             if model.x[i, j, k]():
#                 print(f"{model.x[i, j, k]} = {model.x[i, j, k]()}")
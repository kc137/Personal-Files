# Import Pyomo library and Solver
import pyomo.environ as pyo
from pyomo.opt import SolverFactory
import pandas as pd
from collections import defaultdict

# Model
model = pyo.ConcreteModel()

# Sets
model.CUSTOMERS = pyo.Set(initialize = ['A', 'B', 'C', 'D', 'E', 'F', 'G'])
model.cust = pyo.Set(initialize = ['B', 'C', 'D', 'E', 'F', 'G'])
model.VEHICLES = pyo.Set(initialize = ['V1', 'V2'])

# Parameters
demdata = pd.read_excel("VRP RP1.xlsx", index_col = 0, header = 0, usecols = "A:H", nrows = 7)
# demand = pd.read_excel("VRP RP1.xlsx", header = 9, usecols = "A:H", nrows = 2)
model.demand = pyo.Param(model.CUSTOMERS, initialize = {'A': 0, 'B': 30, 'C': 28, 'D': 40, 'E': 30, 'F': 40, 'G': 50})
model.capacity = pyo.Param(model.VEHICLES, initialize = {'V1': 150, 'V2': 200})
dist = defaultdict(int)

for V in model.VEHICLES:
    dist[V] = 0

model.distance = demdata

# Variables
model.x = pyo.Var(model.CUSTOMERS, model.CUSTOMERS, model.VEHICLES, within=pyo.Binary)
model.u = pyo.Var(model.cust, within=pyo.NonNegativeReals)

# Objective function
def objective_rule(model):
    return sum(model.distance[j][i]*model.x[i, j, k] if j != i else 0
               for k in model.VEHICLES 
               for j in model.CUSTOMERS
                for i in model.CUSTOMERS)
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
model.enter_go = pyo.Constraint(model.cust, model.VEHICLES, rule=enter)

def flow_rule(model, j):
    return sum(model.x[i, j, k]
               for i in model.CUSTOMERS
               for k in model.VEHICLES) == 1
model.flow_constraint = pyo.Constraint(model.cust, rule=flow_rule)

model.depot = pyo.ConstraintList()
for k in model.VEHICLES:
    model.depot.add(sum(model.x["A", j, k] for j in model.cust) == 1)
    model.depot.add(sum(model.x[i, "A", k] for i in model.cust) == 1)

def subtour(model, i, j, k):
    if i != j:
        return model.u[j] - model.u[i] >= model.demand[j] - model.capacity[k]*(1 - model.x[i, j, k])
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
#             print(f"{model.x[i, j, k]} = {model.x[i, j, k]()}")
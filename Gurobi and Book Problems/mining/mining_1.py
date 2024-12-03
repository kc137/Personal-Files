import pyomo.environ as pyo, gurobipy as gp, numpy as np, pandas as pd
from pyomo.opt import SolverFactory

# Params

years = [*range(1, 6)]
mines = [*range(1, 5)]

royalties = {1: 5e6, 2: 4e6, 3: 4e6, 4: 5e6}
capacity = {1: 2e6, 2: 2.5e6, 3: 1.3e6, 4: 3e6}
quality = {1: 1.0, 2: 0.7, 3: 1.5, 4: 0.5}
target = {1: 0.9, 2: 0.8, 3: 1.2, 4: 0.6, 5: 1.0}
time_discount = {year: (1/(1+1/10.0)) ** (year-1) for year in years}

max_mines = 3
price = 10

# Model
model = pyo.ConcreteModel()

# Variables

model.blend = pyo.Var(years, within = pyo.NonNegativeReals)
blend = model.blend

model.extract = pyo.Var(years, mines, within = pyo.NonNegativeReals)
extract = model.extract

model.working = pyo.Var(years, mines, within = pyo.Binary)
working = model.working

model.available = pyo.Var(years, mines, within = pyo.Binary)
available = model.available

# Constraints

"""
The total number of operating mines in year t
cannot exceed the limit.

"""

def operating_mines(model, t):
    return pyo.quicksum(working[t, m] 
                        for m in mines) <= max_mines
model.c1 = pyo.Constraint(years, rule = operating_mines)

"""
The final quality of the ore blended in year t
must meet the target.

"""

def final_quality(model, t):
    return pyo.quicksum(quality[m]*extract[t, m] 
                        for m in mines) == target[t]*blend[t]
model.c2 = pyo.Constraint(years, rule = final_quality)

"""
Total tons of ore extracted in year t
should be equal to the Tons of the ore blended in that year.

"""

def mass_conservation(model, t):
    return pyo.quicksum(extract[t, m] 
                        for m in mines) == blend[t]
model.c3 = pyo.Constraint(years, rule = mass_conservation)

"""
Total tons of ore extracted from mine m
in year t cannot exceed the yearly capacity of that mine.

"""

def mine_capacity(model, t, m):
    return extract[t, m] <= capacity[m]*working[t, m]
model.c4 = pyo.Constraint(years, mines, rule = mine_capacity)

"""
Mine m can be operated in year t only if it is open in that year.
"""

def open_to_operate(model, t, m):
    return working[t, m] <= available[t, m]
model.c5 = pyo.Constraint(years, mines, rule = open_to_operate)

"""
If mine m is closed in year t, it cannot be opened again in the future.

"""

def shut_down(model, t, m):
    if t < years[-1]:
        return available[t+1, m] <= available[t, m]
    else:
        return pyo.Constraint.Skip
model.c6 = pyo.Constraint(years, mines, rule = shut_down)

# Objectivee Function

"""
Note : Seperate the terms when applying sum function for correct 
calculation and accurate results.
"""

def obj_fn(model):
    return (pyo.quicksum(time_discount[t]*price*blend[t] for t in years) 
            - pyo.quicksum(time_discount[t]*royalties[m]*available[t, m] 
                         for t in years 
                         for m in mines))
model.obj = pyo.Objective(rule = obj_fn, sense = pyo.maximize)

# Solution

sol = SolverFactory("cplex")
res = sol.solve(model)

# Printing the Solution

print(res)






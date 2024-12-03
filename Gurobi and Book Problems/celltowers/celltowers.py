import pyomo.environ as pyo, numpy as np, pandas as pd
from pyomo.opt import SolverFactory

tower_coverage = []
population = []
tower_cost = []
budget = 20

with open("regional_data.txt", "r") as data:
    lines = data.read().splitlines()
    
    for line in lines[1:1+6]:
        line_str = line.split()
        tower_coverage.append([int(t) for t in line_str[1:]])
    line_str = lines[8].split()
    population.extend([int(t) for t in line_str[1:]])
    for line in lines[10:10+6]:
        line_str = line.split()
        tower_cost.append(float(line_str[-1]))
# print(tower_coverage)

coverage = {n+1 : [] for n in range(len(population))}
for tower in range(len(tower_coverage)):
    for i in range(len(tower_coverage[tower])):
        if tower_coverage[tower][i]:
            coverage[i+1].append(tower+1)

# Model Definition

model = pyo.ConcreteModel()

# Sets and Parameters

model.T = pyo.RangeSet(1, len(tower_coverage))
model.R = pyo.RangeSet(1, len(tower_coverage[0]))

# Variables

model.x = pyo.Var(model.T, within = pyo.Binary)
x = model.x

model.y = pyo.Var(model.R, within = pyo.Binary)
y = model.y

# Constraints

def cost(model):
    return pyo.quicksum(x[t]*tower_cost[t-1] for t in model.T) <= budget
model.c1 = pyo.Constraint(rule = cost)

# def covered(model, r):
#     return pyo.quicksum(x[t] for t in model.T if r in coverage[t]) >= y[r]
# model.c2 = pyo.Constraint(model.R, rule = covered)

def covered(model, r):
    return pyo.quicksum(x[t] for t in coverage[r]) >= y[r]
model.c2 = pyo.Constraint(model.R, rule = covered)

# Objective Function

def obj_fn(model):
    return pyo.quicksum(
        y[r]*population[r-1]
        for r in model.R
        )
model.obj = pyo.Objective(rule = obj_fn, sense = pyo.maximize)

# Solution

sol = SolverFactory("cplex")
res = sol.solve(model)

# Printing the Solution

print(f"The total Population covered by installing {sum(x[t]() for t in model.T)}-Towers : {model.obj()}.")

for t in model.T:
    if x[t]() and x[t]() >= 0.9:
        print(f"Installed Tower : {t}")
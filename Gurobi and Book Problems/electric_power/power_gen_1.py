import pyomo.environ as pyo, gurobipy as gp
from pyomo.opt import SolverFactory

# Model

model = pyo.ConcreteModel()

model.g_types = pyo.RangeSet(1, 3)
model.periods = pyo.RangeSet(1, 5)
max_start_0 = 5

n_gen = [12, 10, 5]
period_hours = [6, 3, 6, 3, 6]
demand = [15000, 30000, 25000, 40000, 27000]
min_load = [850, 1250, 1500]
max_load = [2000, 1750, 4000]
base_cost = [1000, 2600, 3000]
per_mw_cost = [2, 1.3, 3]
startup_cost = [2000, 1000, 500]

# Variables

model.total_gen = pyo.Var(model.g_types, model.periods, within = pyo.NonNegativeIntegers)
total_gen = model.total_gen

model.n_start = pyo.Var(model.g_types, model.periods, within = pyo.NonNegativeIntegers)
n_start = model.n_start

model.output = pyo.Var(model.g_types, model.periods, within = pyo.NonNegativeReals)
output = model.output

# Available Generators

def avail_gen(model, g, t):
    return total_gen[g, t] <= n_gen[g-1]
model.c1 = pyo.Constraint(model.g_types, model.periods, rule = avail_gen)

def demand_satisfy(model, t):
    return pyo.quicksum(output[g, t] for g in model.g_types) >= demand[t-1]
model.c2 = pyo.Constraint(model.periods, rule = demand_satisfy)

model.min_max = pyo.ConstraintList()

for g in model.g_types:
    for t in model.periods:
        model.min_max.add(
            output[g, t] >= min_load[g-1]*total_gen[g, t]
            )
        model.min_max.add(
            output[g, t] <= max_load[g-1]*total_gen[g, t]
            )

def reserve(model, g, t):
    return pyo.quicksum(max_load[g-1]*total_gen[g, t] for g in model.g_types) >= (1.15*demand[t-1])
model.c4 = pyo.Constraint(model.g_types, model.periods, rule = reserve)

def start_up(model, g, t):
    if t == 1:
        return total_gen[g, t] <= 5 + n_start[g, t]
    else:
        return total_gen[g, t] <= total_gen[g, t-1] + n_start[g, t]
model.c5 = pyo.Constraint(model.g_types, model.periods, rule = start_up)

# Objective Function

def obj_fn(model):
    return (pyo.quicksum(base_cost[g-1]*period_hours[t-1]*total_gen[g, t] 
                         for g in model.g_types 
                         for t in model.periods) + 
            pyo.quicksum(per_mw_cost[g-1]*period_hours[t-1]*(output[g, t] - min_load[g-1]*total_gen[g, t]) 
                         for g in model.g_types 
                         for t in model.periods) + 
            pyo.quicksum(startup_cost[g-1]*n_start[g, t] 
                         for g in model.g_types 
                         for t in model.periods))
model.obj = pyo.Objective(rule = obj_fn, sense = pyo.minimize)

# Solution

sol = SolverFactory("cplex")
res = sol.solve(model)

print(res)










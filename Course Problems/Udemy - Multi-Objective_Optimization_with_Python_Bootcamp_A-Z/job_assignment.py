import pyomo.environ as pyo
from pyomo.opt import SolverFactory

model = pyo.ConcreteModel()

max_hrs = 6

# Sets and Parameters

model.J = pyo.RangeSet(1, 6)
model.D = pyo.RangeSet(1, 3)

profits_list = [200, 500, 300, 100, 1000, 300]

durations_list = [2, 3, 5, 2, 6, 4]

# Variables

model.x = pyo.Var(model.J, model.D, within = pyo.Binary)
x = model.x

# Constraints

def demand_once(model, j):
    return sum(x[j, d] for d in model.D) <= 1
model.c1 = pyo.Constraint(model.J, rule = demand_once)

def max_hours(model, d):
    return sum(x[j, d]*durations_list[j-1] for j in model.J) <= max_hrs
model.c2 = pyo.Constraint(model.D, rule = max_hours)

# Objective Function

def obj_fn(model):
    return sum(x[j, d]*profits_list[j-1] 
               for j in model.J 
               for d in model.D)
model.obj = pyo.Objective(rule = obj_fn, sense = pyo.maximize)

# Solution

sol = SolverFactory("cplex")
res = sol.solve(model)

# Printing the Results

for j in model.J:
    for d in model.D:
        if x[j, d]() and x[j, d]() >= 0.9:
            print(f"Job-{j} completed on Day-{d}, took {durations_list[j-1]} hours "\
                  f"and generated {profits_list[j-1]}-$.")

print(f"The maximum profit generated over 3-days : {model.obj()}")
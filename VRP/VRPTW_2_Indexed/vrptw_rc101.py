import pyomo.environ as pyo
from pyomo.opt import SolverFactory
from rc101_25_data import matrix, time_array, demands, capacity, service_time

model = pyo.ConcreteModel()

M = 2000
NC = len(matrix)

# Sets

model.N = pyo.RangeSet(1, NC)
model.C = pyo.RangeSet(2, NC)
model.V = pyo.RangeSet(1, 9)

# Variables

model.x = pyo.Var(model.N, model.N, model.N, within = pyo.Binary)
x = model.x

model.t = pyo.Var(model.N, model.N, within = pyo.NonNegativeReals)
t = model.t

# Constraints

def once(model, j):
    return sum(x[i, j, k] 
               for i in model.N 
               for k in model.V if i != j) == 1
model.c1 = pyo.Constraint(model.C, rule = once)

def flow(model, j, k):
    return sum(x[i, j, k] for i in model.N if i != j) == sum(x[j, i, k] for i in model.N if i != j)
model.c2 = pyo.Constraint(model.C, model.V, rule = flow)

def demand(model, k):
    return sum(x[i, j, k]*demands[j-1] 
               for i in model.N 
               for j in model.C if i != j) <= capacity
model.c3 = pyo.Constraint(model.V, rule = demand)

def depot(model, j):
    return sum(x[1, j, k] 
               for k in model.V) <= 1
model.c4 = pyo.Constraint(model.C, rule = depot)

def time_windows(model, i, j, k):
    if i != j:
        return t[i, k] + matrix[i-1][j-1] + service_time <= t[j, k] + M*(1 - x[i, j, k]) - 0.0001
    else:
        return pyo.Constraint.Skip
model.c5 = pyo.Constraint(model.N, model.C, model.V, rule = time_windows)

def service1(model, i, k):
    return time_array[i-1][0] <= t[i, k]
model.c6 = pyo.Constraint(model.N, model.V, rule = service1)

def service2(model, i, k):
    return time_array[i-1][1] >= t[i, k]
model.c7 = pyo.Constraint(model.N, model.V, rule = service2)

# Objective Function

def obj_fn(model):
    return sum(x[i, j, k]*matrix[i-1][j-1] 
               for i in model.N 
               for j in model.N 
               for k in model.V if i != j)
model.obj = pyo.Objective(rule = obj_fn, sense = pyo.minimize)

# Solution

sol = SolverFactory("cplex")
sol.options["timelimit"] = 10
res = sol.solve(model)

# Printing the Solution

print(f"Total Distance by all vehicles : {model.obj()} km.")
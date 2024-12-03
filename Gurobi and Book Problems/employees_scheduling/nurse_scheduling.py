import pyomo.environ as pyo, numpy as np
from pyomo.opt import SolverFactory

model = pyo.ConcreteModel()

# Sets and Parameters

model.N = pyo.RangeSet(1, 12)
model.S = pyo.RangeSet(1, 3)
model.D = pyo.RangeSet(1, 7)

not_pre_list = [[2], [1, 3], [1, 2], [], [1], [2], [], [1, 2], [1, 3], [3], [1], [2, 3]]
not_preferred = {n : not_pre_list[n-1] for n in model.N}

nurse_per_shift_list = [[3, 4], [3, 4], [2, 3]]


# Variables

model.x = pyo.Var(model.N, model.D, model.S, within = pyo.Binary)
x = model.x

# Constraints

def consecutive_shifts(model, n, d):
    return pyo.quicksum(x[n, d, s] for s in model.S) <= 1
model.c1 = pyo.Constraint(model.N, model.D, rule = consecutive_shifts)

def five_per_week(model, n):
    return pyo.quicksum(x[n, d, s] 
                        for d in model.D 
                        for s in model.S) <= 5
model.c2 = pyo.Constraint(model.N, rule = five_per_week)

def nurses_per_shift_lb(model, d, s):
    return pyo.quicksum(x[n, d, s] for n in model.N) >= nurse_per_shift_list[s-1][0]
model.c3 = pyo.Constraint(model.D, model.S, rule = nurses_per_shift_lb)

def nurses_per_shift_ub(model, d, s):
    return pyo.quicksum(x[n, d, s] for n in model.N) <= nurse_per_shift_list[s-1][1]
model.c4 = pyo.Constraint(model.D, model.S, rule = nurses_per_shift_ub)

def not_preferred_shifts(model, n, d):
    for s in not_preferred[n]:
        return x[n, d, s] == 0
# model.c5 = pyo.Constraint(model.N, model.D, rule = not_preferred_shifts)

model.not_preferred_shifts = pyo.ConstraintList()

for n in model.N:
    for d in model.D:
        for s in not_preferred[n]:
            model.not_preferred_shifts.add(x[n, d, s] == 0)

# Objective Function

def obj_fn(model):
    return pyo.quicksum(x[n, d, s] 
                        for n in model.N 
                        for d in model.D 
                        for s in model.S)
model.obj = pyo.Objective(rule = obj_fn, sense = pyo.minimize)

# Solution

sol = SolverFactory("cplex")
res = sol.solve(model)

# Printing the Solution

nurse_shift_allocation = np.zeros(shape = [len(model.N), len(model.D), len(model.S)], dtype = int)

for n in model.N:
    for d in model.D:
        for s in model.S:
            if x[n, d, s]() and x[n, d, s]() >= 0.9:
                nurse_shift_allocation[n-1][(d-1)][(s-1)] = x[n, d, s]()

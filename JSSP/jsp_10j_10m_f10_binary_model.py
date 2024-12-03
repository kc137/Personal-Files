import pyomo.environ as pyo
from pyomo.opt import SolverFactory
from jsp_10j_10m_f10_data import machine_sequence as ms, processing_times as pt

model = pyo.ConcreteModel()

M = 2000

# Sets and Parameters

model.m = pyo.RangeSet(1, 10)
model.M = pyo.RangeSet(1, 10)
model.i = pyo.RangeSet(1, 10)
model.j = pyo.RangeSet(1, 10)

model.times = pyo.Param(model.j, model.m, within = pyo.Any, 
                        initialize = {
                            (j, m) : pt[j-1][m-1] 
                            for j in model.j 
                            for m in model.m
                            })
processing_times = model.times

model.m_sequence = pyo.Param(model.j, model.m, within = pyo.Any, 
                        initialize = {
                            (j, m) : ms[j-1][m-1] 
                            for j in model.j 
                            for m in model.m
                            })
machine_sequence = model.m_sequence

# Variables

model.x = pyo.Var(model.m, model.i, model.j, within = pyo.Binary)
x = model.x

model.start = pyo.Var(model.j, model.m, within = pyo.NonNegativeReals)
start = model.start

model.finish = pyo.Var(model.m, within = pyo.NonNegativeReals)
finish = model.finish

model.makespan = pyo.Var(within = pyo.NonNegativeReals)
makespan = model.makespan

# Constraints

def finish_time(model, j, m):
    return start[j, m] + processing_times[j, m] <= finish[m]
model.c1 = pyo.Constraint(model.j, model.m, rule = finish_time)

def start_time(model, j, m, M):
    if m <= 9 and m != M and m > M:
        return start[j, machine_sequence[j, M]] + processing_times[j, machine_sequence[j, M]] <= start[j, machine_sequence[j, m+1]]
    else:
        return pyo.Constraint.Skip
model.c2 = pyo.Constraint(model.j, model.m, model.M, rule = start_time)

def precedence(model, m, i, j):
    if i != j:
        return start[j, m] + processing_times[j, m] - M*(1 - x[m, i, j]) <= start[i, m]
    else:
        return pyo.Constraint.Skip
model.c3 = pyo.Constraint(model.m, model.i, model.m, rule = precedence)

def max_time(model, m):
    return finish[m] <= makespan
model.c4 = pyo.Constraint(model.m, rule = max_time)

# Objective Function

model.obj = pyo.Objective(expr = makespan, sense = pyo.minimize)

# Solution

sol = SolverFactory("cplex")
res = sol.solve(model)

# Printing the Solution

print(f"The makespan for 10-Job 10-Machine instance : {model.obj()}")



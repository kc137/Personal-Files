import pyomo.environ as pyo
from pyomo.opt import SolverFactory

model = pyo.ConcreteModel()

# Sets

model.tasks = pyo.RangeSet(1, 12)
model.machines = pyo.RangeSet(1, 4)

# Params

duration_list = [3, 6, 7, 6, 4, 8, 9, 11, 2, 13, 4, 3]
model.durations = pyo.Param(model.tasks, within = pyo.Any, 
                            initialize = {n : duration_list[n-1] 
                                          for n in model.tasks})

predecessors = {
    1 : [], 
    2 : [1], 
    3 : [1], 
    4 : [2], 
    5 : [2], 
    6 : [2, 3], 
    7 : [3], 
    8 : [6], 
    9 : [4, 5, 8], 
    10 : [8, 11], 
    11 : [7], 
    12 : [9, 10]
    }

operation_seq = []

for task in model.tasks:
    for key in predecessors:
        if task in predecessors[key]:
            operation_seq.append((task, key))

model.operations = pyo.Set(operation_seq)

# for op in model.operations_index:
#     print(op)

# Variables

model.x = pyo.Var(model.tasks, model.machines, within = pyo.Binary)
x = model.x

model.cycle = pyo.Var(within = pyo.NonNegativeReals)
cycle = model.cycle

# Constraints

def machine_once(model, t):
    return sum(x[t, m] for m in model.machines) == 1
model.c1 = pyo.Constraint(model.tasks, rule = machine_once)

def tasks_order(model, i, j):
    return sum(m*x[i, m] for m in model.machines) <= sum(m*x[j, m] for m in model.machines)
model.c2 = pyo.Constraint(operation_seq, rule = tasks_order)

def machine_cycle_time(model, m):
    return sum(x[i, m]*model.durations[i] for i in model.tasks) <= cycle
model.c3 = pyo.Constraint(model.machines, rule = machine_cycle_time)

# Objective Function

model.obj = pyo.Objective(expr = cycle, sense = pyo.minimize)

# Solution

sol = SolverFactory("cplex")
res = sol.solve(model)

# Printing Solution

for m in model.machines:
    cycle_time = 0
    for t in model.tasks:
        if x[t, m]() >= 0.9:
            print(f"{x[t, m]} = {x[t, m]()}")
            cycle_time += model.durations[t]
    print(f"Cycle-time for Machine-{m} : {cycle_time}")
print(f"Total cycle time : {model.obj()} min.")

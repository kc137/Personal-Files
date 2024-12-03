import pyomo.environ as pyo
from pyomo.opt import SolverFactory

with open("batch_to_machine.txt", "r") as data:
    all_data = data.read().splitlines()
    durations_str = [data.split() for data in all_data]
    durations_list = [(int(mbd[0]), int(mbd[1]), int(mbd[2])) for mbd in durations_str[1:51]]
    costs_list = [(int(mbc[0]), int(mbc[1]), int(mbc[2])) for mbc in durations_str[53:103]]
    capacities_list = [(int(mbcp[0]), int(mbcp[1])) for mbcp in durations_str[105:110]]

# Creating Model

model = pyo.ConcreteModel()

# Sets and Paramaters

model.batches = pyo.RangeSet(1, 10)
model.machines = pyo.RangeSet(1, 5)

model.durations = pyo.Param(model.machines, model.batches, within = pyo.Any, 
                            initialize = {
                                (durations_list[i][0], durations_list[i][1]) : durations_list[i][2] 
                                for i in range(len(durations_list))
                                })
durations = model.durations

model.costs = pyo.Param(model.machines, model.batches, within = pyo.Any, 
                            initialize = {
                                (costs_list[i][0], costs_list[i][1]) : costs_list[i][2] 
                                for i in range(len(costs_list))
                                })
costs = model.costs

model.capacities = pyo.Param(model.machines, within = pyo.Any, 
                             initialize = {
                                 capacities_list[i][0] : capacities_list[i][1] 
                                 for i in range(len(capacities_list))
                                 })
capacities = model.capacities

# Variables

model.x = pyo.Var(model.machines, model.batches, within = pyo.Binary)
x = model.x

# Constraints

def capacity(model, m):
    return sum(x[m, b]*durations[m, b] for b in model.batches) <= capacities[m]
model.c1 = pyo.Constraint(model.machines, rule = capacity)

# def total(model):
#     return sum(x[m, b] for m in model.machines for b in model.batches) == len(model.batches)
# model.c2 = pyo.Constraint(rule = total)

def machine_once(model, b):
    return sum(x[m, b] for m in model.machines) == 1
model.c3 = pyo.Constraint(model.batches, rule = machine_once)

# Objective Function

def obj_fn(model):
    return sum(x[m, b]*costs[m, b] for m in model.machines for b in model.batches)
model.obj = pyo.Objective(rule = obj_fn)

# Solution

sol = SolverFactory("cplex")
res = sol.solve(model)

print(res)

for m in model.machines:
    for b in model.batches:
        if x[m, b]():
            print(f"Production batch-{b} is assigned to Machine-{m}")
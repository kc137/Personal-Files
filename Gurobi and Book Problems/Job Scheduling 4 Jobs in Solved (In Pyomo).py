import pyomo.environ as pyo
from pyomo.opt import SolverFactory

model = pyo.ConcreteModel()

# Sets and Parameters

M = 2000
model.i = pyo.RangeSet(1, 4)
model.jobs = pyo.Param(model.i, domain = pyo.Any, initialize = {1 : {"duration" : 6, "due" : 8}, 
        2 : {"duration" : 4, "due" : 4}, 
        3 : {"duration" : 5, "due" : 12}, 
        4 : {"duration" : 8, "due" : 16}})
jobs = model.jobs

machines = [i for i in model.i]

# Variables

model.start = pyo.Var(model.i, domain = pyo.NonNegativeReals)
start = model.start

model.x = pyo.Var(model.i, model.i, domain = pyo.Binary)
x = model.x

model.ymax = pyo.Var(domain = pyo.NonNegativeReals)
ymax = model.ymax

# model.c = pyo.Var(model.i, domain = pyo.NonNegativeIntegers)
# c = model.c

model.c = pyo.Var(model.i, domain = pyo.NonNegativeReals)
c = model.c

model.y = pyo.Var(model.i, domain = pyo.NonNegativeReals)
y = model.y

# Constraints

model.Clst = pyo.ConstraintList()
for i in model.i:
    model.Clst.add(c[i] >= jobs[i]["duration"])
    model.Clst.add(y[i] >= c[i] - jobs[i]["due"])

for i in model.i:
    for k in model.i:
        if i != k:
            model.Clst.add(c[k] + jobs[i]["duration"] <= c[i] + M*x[i, k])

for i in model.i:
    for k in model.i:
        if i != k:
            model.Clst.add(c[i] + jobs[k]["duration"] <= c[k] + M*(1 - x[i, k]))
            # model.Clst.add(start[i] >= c[i])


# Objective Function

def Obj_Fn(model):
    return sum(y[i] for i in model.i)
model.Obj = pyo.Objective(rule = Obj_Fn, sense = pyo.minimize)

# Solution

sol = SolverFactory("glpk")
res = sol.solve(model)

for i in model.i:
    print(f"Completion Time - {i} : {c[i]()}")

total_delay = 0
for i in model.i:
    if c[i]() - jobs[i]["due"] > 0:
        print(f"Delay for Job-{i} : {c[i]() - jobs[i]['due']}")
        total_delay += c[i]() - jobs[i]["due"]
    else:
        print(f"Delay for Job-{i} : 0")

machine_run = []
completion = []
for i in model.i:
    completion.append((i, c[i]()))
    
completion.sort(key = lambda x : x[1])

for c in completion:
    machine_run.append(c[0])

print("Jobs will run in order:\n")
for i in range(len(machine_run)):
    if i == 0:
        print(f"{machine_run[i]}", end = " ")
    else:
        print(f"--> {machine_run[i]}", end = " ")
    

print(f"\n\nTotal Delay : {total_delay}")
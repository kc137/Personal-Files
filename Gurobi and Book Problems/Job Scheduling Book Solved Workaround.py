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
duration = {1 : 8, 2 : 4, 3 : 12, 4 : 16}
dur = sorted(duration.items(), key = lambda x : x[1])
duration = []
for key in dur:
    duration.append(key[0])
    
flow = []
flowtime = 0
for d in duration:
    flowtime += jobs[d]["duration"]
    flow.append(flowtime)

# Variables

model.start = pyo.Var(model.i, domain = pyo.NonNegativeReals)
start = model.start

model.x = pyo.Var(model.i, model.i, domain = pyo.Binary)
x = model.x

model.ymax = pyo.Var(domain = pyo.NonNegativeReals)
ymax = model.ymax

model.c = pyo.Var(model.i, domain = pyo.NonNegativeReals)
c = model.c

model.y = pyo.Var(model.i, domain = pyo.NonNegativeReals)
y = model.y

# Constraints

model.Clst = pyo.ConstraintList()

for i in model.i:
    model.Clst.add(y[i] == c[i] - jobs[i]["due"])
    model.Clst.add(y[i] >= 0)


model.Obj = pyo.Objective(expr = sum(y[i] for i in model.i), sense = pyo.minimize)

sol = SolverFactory("couenne")
res = sol.solve(model)

print(f"Minimized total delay : {model.Obj()}")















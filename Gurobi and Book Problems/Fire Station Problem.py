import pyomo.environ as pyo, pandas as pd
from pyomo.opt import SolverFactory

model = pyo.ConcreteModel()

# Sets and Parameters

model.i = pyo.RangeSet(1, 6)
model.j = pyo.RangeSet(1, 6)

time = [[0, 10, 20, 30, 30, 20], 
        [10, 0, 25, 35, 20, 10], 
        [20, 25, 0, 15, 30, 20], 
        [30, 35, 15, 0, 15, 25], 
        [30, 20, 30, 15, 0, 14], 
        [20, 10, 20, 25, 14, 0]]

times = pd.DataFrame(time, index = [1, 2, 3, 4, 5, 6], columns = [1, 2, 3, 4, 5, 6])

# Variables

model.x = pyo.Var(model.i, domain = pyo.Binary)
x = model.x

# Constraints

model.time_cons = pyo.ConstraintList()

for i in model.i:
    timec = 0
    for j in model.j:
        if times[j][i] <= 15:
            timec += x[j]
    model.time_cons.add(timec >= 1)

# Objective Function

def Obj_Fn(model):
    return sum(x[i] for i in model.i)
model.Obj = pyo.Objective(rule = Obj_Fn, sense = pyo.minimize)

# Results

sol = SolverFactory("cplex")
res = sol.solve(model)

print(res)
for i in model.i:
    if x[i]():
        print(f"City-{i} has a fire station")
print(f"Total no. of fire stations are: {model.Obj()}")
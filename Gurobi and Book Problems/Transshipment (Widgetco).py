import pyomo.environ as pyo, pandas as pd, numpy as np
from pyomo.opt import SolverFactory

model = pyo.ConcreteModel()

# Sets

model.i = pyo.RangeSet(1, 4)
model.j = pyo.RangeSet(1, 5)

# Parameters

dat1 = {1 : [8, 15, 0, 6], 2 : [13, 12, 6, 0], 3 : [25, 26, 16, 14], 
        4 : [28, 25, 17, 16], 5 : [0, 0, 0, 0]}
data = pd.DataFrame(dat1)
data.index += 1

model.S = pyo.Param(model.i, initialize = {1 : 150, 2 : 200})
S = model.S
model.D = pyo.Param(model.j, initialize = {1 : 130, 2 : 130})
D = model.D

# Vars

model.x = pyo.Var(model.i, model.j, domain = pyo.NonNegativeIntegers)
x = model.x

# Constraints

# Supply Constraints

def Cons1(model, j):
    return sum(x[1, j] for j in model.j) <= S[1]
model.C1 = pyo.Constraint(rule = Cons1)

def Cons2(model, j):
    return sum(x[2, j] for j in model.j) <= S[2]
model.C2 = pyo.Constraint(rule = Cons2)

def Cons3(model, j):
    return sum(x[3, j] for j in model.j) <= 350
model.C3 = pyo.Constraint(rule = Cons3)

def Cons4(model, j):
    return sum(x[4, j] for j in model.j) <= 350
model.C4 = pyo.Constraint(rule = Cons4)

# Demand Constraints

def Cons5(model, j):
    return sum(x[i, 1] for i in model.i) == 350
model.C5 = pyo.Constraint(rule = Cons5)

def Cons6(model, j):
    return sum(x[i, 2] for i in model.i) == 350
model.C6 = pyo.Constraint(rule = Cons6)

def Cons7(model, j):
    return sum(x[i, 3] for i in model.i) == 130
model.C7 = pyo.Constraint(rule = Cons7)

def Cons8(model, j):
    return sum(x[i, 4] for i in model.i) == 130
model.C8 = pyo.Constraint(rule = Cons8)

def Cons9(model, j):
    return sum(x[i, 5] for i in model.i) == 90
model.C9 = pyo.Constraint(rule = Cons9)

# Objective Function

def Obj_Fn(model):
    return sum(x[i, j]*data[j][i] for i in model.i for j in model.j)
model.Obj = pyo.Objective(rule = Obj_Fn, sense = pyo.minimize)

sol = SolverFactory("couenne")
res = sol.solve(model)

for i in model.i:
    for j in model.j:
        if x[i, j]():
            print("x", i, j, "=", np.round(x[i, j]()))

print("The minimized cost is", model.Obj())
# model.pprint()
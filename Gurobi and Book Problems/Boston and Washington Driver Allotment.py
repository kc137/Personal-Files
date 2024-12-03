import pyomo.environ as pyo, pandas as pd, numpy as np
from pyomo.opt import SolverFactory

model = pyo.ConcreteModel()

# Sets

model.i = pyo.RangeSet(1, 5)
model.j = pyo.RangeSet(1, 5)

# Parameters

dat1 = {1 : [23.5, 22, 18, 10.5, 19], 2 : [21, 22.5, 21.5, 10, 15.5], 
        3 : [15, 16.5, 20.5, 20, 14.5], 4 : [11.5, 11, 17, 23.5, 18], 
        5 : [18, 16.5, 11.5, 19, 23.5]}
data = pd.DataFrame(dat1)
data.index += 1

# Variables

model.x = pyo.Var(model.i, model.j, within = pyo.Binary)
x = model.x

# Washington Constraints

def Cons1(model, j):
    return sum(x[1, j] for j in model.j) == 1
model.C1 = pyo.Constraint(rule = Cons1)

def Cons2(model, j):
    return sum(x[2, j] for j in model.j) == 1
model.C2 = pyo.Constraint(rule = Cons2)

def Cons3(model, j):
    return sum(x[3, j] for j in model.j) == 1
model.C3 = pyo.Constraint(rule = Cons3)

def Cons4(model, j):
    return sum(x[4, j] for j in model.j) == 1
model.C4 = pyo.Constraint(rule = Cons4)

def Cons5(model, j):
    return sum(x[5, j] for j in model.j) == 1
model.C5 = pyo.Constraint(rule = Cons5)

# Boston Constraints

def Cons6(model, i):
    return sum(x[i, 1] for i in model.i) == 1
model.C6 = pyo.Constraint(rule = Cons6)

def Cons7(model, i):
    return sum(x[i, 2] for i in model.i) == 1
model.C7 = pyo.Constraint(rule = Cons7)

def Cons8(model, i):
    return sum(x[i, 3] for i in model.i) == 1
model.C8 = pyo.Constraint(rule = Cons8)

def Cons9(model, i):
    return sum(x[i, 4] for i in model.i) == 1
model.C9 = pyo.Constraint(rule = Cons9)

def Cons10(model, i):
    return sum(x[i, 5] for i in model.i) == 1
model.C10 = pyo.Constraint(rule = Cons10)

# Obj Function

def Obj_Fn(model):
    return sum(x[i, j]*data[j][i] for i in model.i for j in model.j)
model.Obj = pyo.Objective(rule = Obj_Fn, sense = pyo.minimize)

# model.pprint()

sol = SolverFactory("couenne")
res = sol.solve(model)

for i in model.i:
    for j in model.j:
        if x[i, j]():
            print("Driver of Boston", i, "is chosen for Washington D.C", j)

print("Total travel time after minimizing downtime of drivers is", model.Obj())
import pyomo.environ as pyo, numpy as np, pandas as pd
from pyomo.opt import SolverFactory

model = pyo.ConcreteModel()

M = 10000

# Sets

model.i = pyo.RangeSet(1, 5)
model.j = pyo.RangeSet(1, 5)

# Parameters

dat1 = {1 : [22, 18, 26, 16, 21], 2 : [18, M, 20, 22, M], 3 : [30, 27, 28, M, 25], 4 : [18, 22, 28, 14, 28], 5 : [0, 0, 0, 0, 0]}
data = pd.DataFrame(dat1, index = [1, 2, 3, 4, 5])

# Variables

model.x = pyo.Var(model.i, model.j, domain = pyo.Binary)
x = model.x

# Constraints

# Machine Constraints

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

# # Job Constraints

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

# Objective Function

def Obj_Fn(model):
    return sum(x[i, j]*data[j][i] for i in model.i for j in model.j)
model.Obj = pyo.Objective(rule = Obj_Fn, sense = pyo.minimize)

# Solution

sol = SolverFactory("glpk")
res = sol.solve(model)

for i in model.i:
    for j in model.j:
        if np.round(x[i, j]()) and j != 5:
            print("Employee", i, "is used for Job", j)
print("Total time to complete all the job is", model.Obj())

for i in model.i:
    for j in model.j:
        if np.round(x[i, j]()) and j != 5:
            print("x", i, j, np.round(x[i, j]()))

# model.pprint()
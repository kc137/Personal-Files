import pyomo.environ as pyo, numpy as np, pandas as pd
from pyomo.opt import SolverFactory

model = pyo.ConcreteModel()

cities = {1 : "Customer 1", 2 : "Customer 2", 3 : "Customer 3"}
warehouses = {1 : "Plant 1", 2 : "Plant 2", 3 : "Plant 3"}

# Sets

model.i = pyo.RangeSet(1, 4)
model.j = pyo.RangeSet(1, 3)

# Parameters

dat1 = {1 : [75, 79, 85, 0], 2 : [60, 63, 76, 0], 3 : [25, 40, 110, 0]}
data = pd.DataFrame(dat1, index = [1, 2, 3, 4])
model.S = pyo.Param(model.i, initialize = {1 : 50, 2 : 100, 3 : 50})
S = model.S
model.D = pyo.Param(model.j, initialize = {1 : 80, 2 : 90, 3 : 100})
D = model.D

# Variables

model.x = pyo.Var(model.i, model.j, domain = pyo.NonNegativeIntegers)
x = model.x

# Constraints

def Cons1(model):
    return sum(x[1, j] for j in model.j) <= S[1]
model.C1 = pyo.Constraint(rule = Cons1)

def Cons2(model):
    return sum(x[2, j] for j in model.j) <= S[2]
model.C2 = pyo.Constraint(rule = Cons2)

def Cons3(model):
    return sum(x[3, j] for j in model.j) <= S[3]
model.C3 = pyo.Constraint(rule = Cons3)

def Cons4(model):
    return sum(x[i, 1] for i in model.i) == D[1]
model.C4 = pyo.Constraint(rule = Cons4)

def Cons5(model):
    return sum(x[i, 2] for i in model.i) == D[2]
model.C5 = pyo.Constraint(rule = Cons5)

def Cons6(model):
    return sum(x[i, 3] for i in model.i) == D[3]
model.C6 = pyo.Constraint(rule = Cons6)

# def Cons7(model):
#     return sum(x[4, j] for j in model.j) <= sum(D[j] for j in model.j) - sum(S[j] for j in model.j)
# model.C7 = pyo.Constraint(rule = Cons7)

# Objective

def Obj_Fn(model):
    return sum(x[i, j]*data[j][i] for i in model.i for j in model.j)
model.Obj = pyo.Objective(rule = Obj_Fn, sense = pyo.maximize)

sol = SolverFactory("couenne")
res = sol.solve(model)

print("Total cost of transportation from Plant to Customer :", model.Obj())

for i in model.i:
    for j in model.j:
        if x[i, j]():
            if i == 4:
                print("Picture Tubes supplied from dummy Plant", i, "to Customer", j, "=", x[i, j]())
            else:
                print("Picture Tubes supplied from Plant", i, "to Customer", j, "=", x[i, j]())
            

import pyomo.environ as pyo, numpy as np, pandas as pd
from pyomo.opt import SolverFactory

model = pyo.ConcreteModel()

cities = {1 : "Customer 1", 2 : "Customer 2", 3 : "Customer 3"}
warehouses = {1 : "Warehouse 1", 2 : "Warehouse 2", 3 : "Warehouse 3"}

# Sets

model.i = pyo.RangeSet(1, 3)
model.j = pyo.RangeSet(1, 3)

# Parameters

dat1 = {1 : [15, 10, 90], 2 : [35, 50, 80], 3 : [25, 40, 110]}
data = pd.DataFrame(dat1, index = [1, 2, 3])
model.S = pyo.Param(model.i, initialize = {1 : 40, 2 : 30})
S = model.S
model.D = pyo.Param(model.j, initialize = {1 : 30, 2 : 30, 3 : 30})
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
    return sum(x[i, 1] for i in model.i) == D[1]
model.C3 = pyo.Constraint(rule = Cons3)

def Cons4(model):
    return sum(x[i, 2] for i in model.i) == D[2]
model.C4 = pyo.Constraint(rule = Cons4)

def Cons5(model):
    return sum(x[i, 3] for i in model.i) == D[3]
model.C5 = pyo.Constraint(rule = Cons5)

# Objective

def Obj_Fn(model):
    return sum(x[i, j]*data[j][i] for i in model.i for j in model.j)
model.Obj = pyo.Objective(rule = Obj_Fn, sense = pyo.minimize)

sol = SolverFactory("couenne")
res = sol.solve(model)

print("Total cost of transportation from Warehouse to Customer :", model.Obj())

for i in model.i:
    for j in model.j:
        if x[i, j]():
            if i == 3:
                print("Gallons supplied from dummy Warehouse", i, "to Customer", j, "=", x[i, j]())
            else:
                print("Gallons supplied from Warehouse", i, "to Customer", j, "=", x[i, j]())
            

import pyomo.environ as pyo, numpy as np, pandas as pd
from pyomo.opt import SolverFactory

model = pyo.ConcreteModel()

data_cols = {1 : "Wine", 2 : "Beer", 3 : "Champagne", 4 : "Whiskey"}
data_rows = ["Molding Time", "Packaging Time", "Glass", "Selling Price"]

# Sets

model.i = pyo.RangeSet(1, 4)

# Parameters

dat = {1 : [4, 1, 3, 6], 2 : [9, 1, 4, 10], 
        3 : [7, 3, 2, 9], 4 : [10, 40, 1, 20]}
data = pd.DataFrame(dat)
data.index += 1

# Variables

model.x = pyo.Var(model.i, within = pyo.NonNegativeIntegers, bounds = (0, None))
x = model.x

# Constraints

def Cons1(model):
    return sum(data[i][1]*x[i] for i in model.i) <= 600
model.C1 = pyo.Constraint(rule = Cons1)

def Cons2(model):
    return sum(data[i][2]*x[i] for i in model.i) <= 400
model.C2 = pyo.Constraint(rule = Cons2)

def Cons3(model):
    return sum(data[i][3]*x[i] for i in model.i) <= 500
model.C3 = pyo.Constraint(rule = Cons3)


# Objective Funciton

def Obj_Fn(model):
    return sum(data[i][4]*x[i] for i in model.i)
model.Obj = pyo.Objective(rule = Obj_Fn, sense = pyo.maximize)

sol = SolverFactory("couenne")
res = sol.solve(model)

for i in model.i:
    print("The manufactured", data_cols[i], "units are", x[i]())

print("The maximized revenut of Glassco company is", model.Obj())
import pyomo.environ as pyo, pandas as pd, numpy as np
from pyomo.opt import SolverFactory

model = pyo.ConcreteModel()

data = pd.read_excel("Oil Data.xlsx", sheet_name = "Sheet1", usecols = "A:L", nrows = 3)
data.index += 1

# Parameters Definition

OC = data["OC"]
PC = data["PC"]
MK = data["MK"]
SP = data["SP"]
RA = data["RA"]
Y = data["Y"]
LU = data["LU"]
SC = data["SC"]
PS = data["PS"]

# Sets

model.i = pyo.Set(initialize = [i for i in data["Product"]])

model.j = pyo.Set(initialize = model.i)

# Variables

model.x = pyo.Var(model.i, within = pyo.NonNegativeReals)
x = model.x

# Objective Function

def Obj_Fn(model, i):
    return (sum(x[i]*LU[i]*(SP[i] - ((x[i]*LU[i]) / (100*RA[i]))) for i in model.i)
            - sum(x[i]*LU[i]*OC[i] for i in model.i)
            - sum(x[i]*PC[i] for i in model.i)
            - sum(x[i]*LU[i]*SC[i]*(1 + (Y[i]*(x[i]*LU[i] / (sum(x[j]*LU[j] for j in model.j)))))
            for i in model.i))

model.Obj = pyo.Objective(rule = Obj_Fn, sense = pyo.maximize)

# Constraints

def Cons1(model, i):
    return sum(x[i] / PS[i] for i in model.i) <= 20

model.C1 = pyo.Constraint(model.i, rule = Cons1)

def Cons2(model, i):
    return x[1]*LU[1] >= MK[1] # Correct should be x[1]*LU[1] >= MK[1]

model.C2 = pyo.Constraint(model.i, rule = Cons2)

def Cons3(model, i):
    return x[2]*LU[2] >= MK[2] # Correct should be x[2]*LU[2] >= MK[2]

model.C3 = pyo.Constraint(model.i, rule = Cons3)

def Cons4(model, i):
    return x[3]*LU[3] >= MK[3] # Correct should be x[3]*LU[3] >= MK[3]

model.C4 = pyo.Constraint(model.i, rule = Cons4)

Sol = SolverFactory("couenne")
res = Sol.solve(model)

# print("Max. Profit from Sales of different types Olive Oil =", np.round(model.Obj(), 3), "$")

# for i in model.i:
#     print("Units of", data["Descriptive Name"][i], "Produced =", np.round(x[i]()), "Units")
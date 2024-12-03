import pyomo.environ as pyo, pandas as pd, numpy as np
from pyomo.opt import SolverFactory

model = pyo.ConcreteModel()

# Sets

model.i = pyo.RangeSet(1, 3)

# Parameters

data = pd.read_excel("S7P3_Data.xlsx", index_col = 0, header = 0, usecols = "A:J", nrows = 3)

Co = data["Co"]
Cp = data["Cp"]
alpha = data["alpha"]
beta = data["beta"]
gamma = data["gamma"]
a = data["a"]
b = data["b"]
c = data["c"]
Pmax = data["Pmax"]

model.Vt = pyo.Param(initialize = 350)
Vt = model.Vt

model.dPmax = pyo.Param(initialize = 400)
dPmax = model.dPmax

model.Wmax = pyo.Param(initialize = 2950)
Wmax = model.Wmax

model.Npmax = pyo.Param(initialize = 3)
Npmax = model.Npmax

model.Nsmax = pyo.Param(initialize = 3)
Nsmax = model.Nsmax

# Variables

# Binary

model.z = pyo.Var(model.i, within = pyo.Binary)
z = model.z

# Positive Integers

model.Np = pyo.Var(model.i, within = pyo.NonNegativeIntegers, bounds = (0, 3))
Np = model.Np

model.Ns = pyo.Var(model.i, within = pyo.NonNegativeIntegers, bounds = (0, 3))
Ns = model.Ns

# Positive Reals

model.x = pyo.Var(model.i, within = pyo.NonNegativeReals, bounds = (0, 1))
x = model.x

model.v = pyo.Var(model.i, within = pyo.NonNegativeReals, bounds = (0, Vt))
v = model.v

model.w = pyo.Var(model.i, within = pyo.NonNegativeReals, bounds = (0, Wmax))
w = model.w

def Power_max(model, i):
    return (0, data["Pmax"][i])

model.P = pyo.Var(model.i, within = pyo.NonNegativeReals, bounds = Power_max)
P = model.P

model.dP = pyo.Var(model.i, within = pyo.NonNegativeReals, bounds = (0, dPmax))
dP = model.dP

# Objective Function

def Obj_Fn(model, i):
    return sum(((data["Co"][i]) + data["Cp"][i]*P[i])*Np[i]*Ns[i]*z[i] for i in model.i)

model.Obj = pyo.Objective(rule = Obj_Fn, sense = pyo.minimize)

# Constraints

def Cons1(model, i):
    return sum(x[i] for i in model.i) == 1

model.C1 = pyo.Constraint(model.i, rule = Cons1)

def Cons2(model, i):
    return (P[i] - ((data["alpha"][i])*(w[i] / Wmax)**3)
            - ((data["beta"][i]*v[i])*(w[i] / Wmax)**2)
            - ((data["gamma"][i]*v[i]**2)*(w[i] / Wmax))) == 0

model.C2 = pyo.Constraint(model.i, rule = Cons2)

def Cons3(model, i):
    return (dP[i] - ((data["a"][i])*(w[i] / Wmax)**2)
            - ((data["b"][i]*v[i])*(w[i] / Wmax))
            - ((data["c"][i])*v[i]**2)) == 0

model.C3 = pyo.Constraint(model.i, rule = Cons3)

def Cons4(model, i):
    return v[i]*Np[i] - x[i]*Vt == 0

model.C4 = pyo.Constraint(model.i, rule = Cons4)

def Cons5(model, i):
    return dPmax*z[i] - dP[i]*Ns[i] == 0

model.C5 = pyo.Constraint(model.i, rule = Cons5)

def Cons6(model, i):
    return P[i] <= z[i]*Pmax[i] 

model.C6 = pyo.Constraint(model.i, rule = Cons6)

def Cons7(model, i):
    return dP[i] <= z[i]*dPmax

model.C7 = pyo.Constraint(model.i, rule = Cons7)

def Cons8(model, i):
    return v[i] <= z[i]*Vt

model.C8 = pyo.Constraint(model.i, rule = Cons8)

def Cons9(model, i):
    return w[i] <= z[i]*Wmax

model.C9 = pyo.Constraint(model.i, rule = Cons9)

def Cons10(model, i):
    return Np[i] <= z[i]*Npmax

model.C10 = pyo.Constraint(model.i, rule = Cons10)

def Cons11(model, i):
    return Ns[i] <= z[i]*Nsmax

model.C11 = pyo.Constraint(model.i, rule = Cons11)

def Cons12(model, i):
    return x[i] <= z[i]

model.C12 = pyo.Constraint(model.i, rule = Cons12)

sol = SolverFactory("mindtpy")
res = sol.solve(model, mip_solver = "glpk", nlp_solver = "ipopt")

# sol = SolverFactory("bonmin")
# res = sol.solve(model)

print("The cost of operating centrifugal pumps annually is", model.Obj())
for i in model.i:
    print("Power", i, "is =", P[i]())
    print('Number of Parallel Lines at Level ',i,'is = ',Np[i]())
    print('Number of Pumps in Each Line at Level ',i,'is = ',Ns[i]())









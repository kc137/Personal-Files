import pyomo.environ as pyo, numpy as np, pandas as pd, math
from pyomo.opt import SolverFactory

model = pyo.ConcreteModel()


# Sets

model.i = pyo.RangeSet(1, 15)

# Parameters

W = pd.read_excel("S7P2_Data.xlsx", sheet_name = "Sheet1", index_col = 0, header =0, usecols = "A:B", nrows = 15)

model.Pload = pyo.Param(initialize = 300)
Pload = model.Pload

model.Pmax = pyo.Param(initialize = 1000)
Pmax = model.Pmax

model.defml = pyo.Param(initialize = 1.25)
defml = model.defml

model.defmax = pyo.Param(initialize = 6)
defmax = model.defmax

model.Dcm = pyo.Param(initialize = 3)
Dcm = model.Dcm

model.Lmax = pyo.Param(initialize = 14)
Lmax = model.Lmax

model.dWmin = pyo.Param(initialize = 0.2)
dWmin = model.dWmin

model.S = pyo.Param(initialize = 234.44e3)
S = model.S

model.G = pyo.Param(initialize = 11.6e6)
G = model.G

# Variables

# Binary

model.x = pyo.Var(model.i, domain = pyo.Binary)
x = model.x

# +ve Integer

model.N = pyo.Var(domain = pyo.NonNegativeIntegers, bounds = (1, None))
N = model.N

# +ve Real

model.dW = pyo.Var(domain = pyo.NonNegativeReals, bounds = (0.2, None))
dW = model.dW

model.Dc = pyo.Var(domain = pyo.NonNegativeReals, bounds = (2*dWmin, Dcm))
Dc = model.Dc

model.defl = pyo.Var(domain = pyo.NonNegativeReals, bounds = (defml / (Pmax - Pload), defmax))
defl = model.defl

model.C = pyo.Var(domain = pyo.NonNegativeReals, bounds = (3, None))
C = model.C

model.K = pyo.Var(domain = pyo.NonNegativeReals, bounds = (None, (Pmax - Pload) / defml))
K = model.K

# Obj Function

# def Obj_Fn(model, i):
#     return math.pi*Dc

def Objective_rule(model):
  return math.pi*Dc*(dW**2)*(N+2)/4
model.Obj = pyo.Objective(rule=Objective_rule,sense=pyo.minimize)


# Constraints

def Cons1(model):
    return C == (Dc / dW)

model.C1 = pyo.Constraint(rule = Cons1)

def Cons2(model):
    return K == ((4*C - 1) / (4*C - 4)) + (0.615 / C)

model.C2 = pyo.Constraint(rule = Cons2)

def Cons3(model):
    return S >= ((8*K*Pmax*Dc) / (math.pi*dW**3))

model.C3 = pyo.Constraint(rule = Cons3)

def Cons4(model):
    return defl == (8*(Dc**3)*N)/(G*dW**2)

model.C4 = pyo.Constraint(rule = Cons4)

def Cons5(model):
    return Pmax*defl + 1.05*(N+2)*(dW) <= Lmax

model.C5 = pyo.Constraint(rule = Cons5)

def Cons6(model, i):
    return dW == sum(W["D"][i]*x[i] for i in model.i)

model.C6 = pyo.Constraint(rule = Cons6)

def Cons7(model, i):
    return sum(x[i] for i in model.i) == 1

model.C7 = pyo.Constraint(rule = Cons7)

# Solver = SolverFactory("mindtpy")
# results = Solver.solve(model, mip_solver = "glpk", nlp_solver = "ipopt")

Solver = SolverFactory("couenne")
results = Solver.solve(model)

print("The design of the Coil Compression is complete.\nThe minimum volume is", model.Obj())
print('Number of Coils = ', N())
print('Coil Spring Diameter is= ',Dc())
for i in model.i:
    if x[i]():
        print("Wire Type is", i, "and Wire Dia. is", W["D"][i])
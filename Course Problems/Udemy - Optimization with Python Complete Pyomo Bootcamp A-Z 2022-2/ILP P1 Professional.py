import pyomo.environ as pyo
from pyomo.opt import SolverFactory

model = pyo.ConcreteModel()

pro = ["Shirts", "Shorts", "Pants"]
Fixed_Costs = [200, 150, 100]

# Sets

model.i = pyo.Set(initialize = pro)

# Params

model.P = pyo.Param(model.i, initialize = {pro[0] : 12, pro[1] : 8, pro[2] : 15})
P = model.P

model.Co = pyo.Param(model.i, initialize = {pro[0] : 6, pro[1] : 4, pro[2] : 8})
Co = model.Co

model.L = pyo.Param(model.i, initialize = {pro[0] : 3, pro[1] : 2, pro[2] : 6})
L = model.L

model.C = pyo.Param(model.i, initialize = {pro[0] : 4, pro[1] : 3, pro[2] : 4})
C = model.C

model.F = pyo.Param(model.i, initialize = {pro[0] : 200, pro[1] : 150, pro[2] : 100})
F = model.F

model.M = pyo.Param(model.i, initialize = {pro[0] : 200, pro[1] : 150, pro[2] : 100})
M = model.M

# Vars

model.x = pyo.Var(model.i, within = pyo.NonNegativeIntegers)
x = model.x
model.y = pyo.Var(model.i, within = pyo.Binary)
y = model.y

# Constraints

def Constraint1(model):
    return sum(L[i]*x[i] for i in model.i) <= 150
model.C1 = pyo.Constraint(rule = Constraint1)

def Constraint2(model):
    return sum(C[i]*x[i] for i in model.i) <= 160
model.C2 = pyo.Constraint(rule = Constraint2)

def Constraint3(model, i):
    return (x[i] <= M[i]*y[i])
model.C3 = pyo.Constraint(model.i, rule = Constraint3)

# Obj Function

def Obj_Fn(model, i):
    return sum(P[i]*x[i] for i in model.i) - sum(Co[i]*x[i] for i in model.i) - sum(F[i]*y[i] for i in model.i)

model.Obj = pyo.Objective(rule = Obj_Fn, sense = pyo.maximize)

Sol = SolverFactory("couenne", executable = "F:\\Solvers\\couenne\\bin\\couenne.exe")
Res = Sol.solve(model)

print("Obj Function :", model.Obj())
for i in model.i:
    print("Total", i, "Produced/Week =", x[i]())
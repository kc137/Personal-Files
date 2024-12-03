import pyomo.environ as pyo
from pyomo.opt import SolverFactory

model = pyo.ConcreteModel()

# Sets

model.j = pyo.Set(initialize = ["Desks", "Tables", "Chairs"])

# Params

model.L = pyo.Param(model.j, initialize = {"Desks" : 8, "Tables" : 6, "Chairs" : 1})
L = model.L
model.F = pyo.Param(model.j, initialize = {"Desks" : 4, "Tables" : 2, "Chairs" : 1.5})
F = model.F
model.C = pyo.Param(model.j, initialize = {"Desks" : 2, "Tables" : 1.5, "Chairs" : 0.5})
C = model.C
model.P = pyo.Param(model.j, initialize = {"Desks" : 60, "Tables" : 30, "Chairs" : 20})
P = model.P

# Vars

model.x = pyo.Var(model.j, within = pyo.NonNegativeReals)
x = model.x

# Obj Function

def Obj_Fn(model):
    return sum(P[i]*x[i] for i in model.j)

model.Obj = pyo.Objective(rule = Obj_Fn, sense = pyo.maximize)

# Constraints

def Constraint1(model, j):
    return sum(L[i]*x[i] for i in model.j) <= 48

model.C1 = pyo.Constraint(model.j, rule = Constraint1)

def Constraint2(model, j):
    return sum(F[i]*x[i] for i in model.j) <= 20

model.C2 = pyo.Constraint(model.j, rule = Constraint2)

def Constraint3(model, j):
    return sum(C[i]*x[i] for i in model.j) <= 8

model.C3 = pyo.Constraint(model.j, rule = Constraint3)

def Constraint4(model, j):
    return x["Table"] <= 5

Sol = SolverFactory("glpk")
res = Sol.solve(model)

print("Obj Function is :", pyo.value(model.Obj))
for i in model.j:
    print("Total", i, "produced :", pyo.value(x[i]))
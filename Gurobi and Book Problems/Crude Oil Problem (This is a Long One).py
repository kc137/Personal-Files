import pyomo.environ as pyo, numpy as np
from pyomo.opt import SolverFactory

model = pyo.ConcreteModel()

# Sets

model.i = pyo.RangeSet(1, 3)
model.j = pyo.RangeSet(1, 3)

# Parameters

model.PP = pyo.Param(model.i, initialize = {1 : 45, 2 : 35, 3 : 25}) # Crude (model.i)
PP = model.PP

model.SP = pyo.Param(model.j, initialize = {1 : 70, 2 : 60, 3 : 50}) # Gasoline (model.j)
SP = model.SP

model.demand = pyo.Param(model.j, initialize = {1 : 3000, 2 : 2000, 3 : 1000})
demand = model.demand

model.octane = pyo.Param(model.i, initialize = {1 : 12, 2 : 6, 3 : 8})
octane = model.octane

model.sulphur = pyo.Param(model.i, initialize = {1 : 0.5, 2 : 2, 3 : 3})
sulphur = model.sulphur

# Variables

model.a = pyo.Var(model.j, within = pyo.NonNegativeReals)
a = model.a

model.x = pyo.Var(model.i, model.j, within = pyo.NonNegativeReals)
x = model.x

# Constraints

def Cons1(model, i):
    return sum(x[i, 1] for i in model.i) == demand[1] + 10*a[1]
model.C1 = pyo.Constraint(rule = Cons1)

def Cons2(model, i):
    return sum(x[i, 2] for i in model.i) == demand[2] + 10*a[2]
model.C2 = pyo.Constraint(rule = Cons2)

def Cons3(model, i):
    return sum(x[i, 3] for i in model.i) == demand[3] + 10*a[3]
model.C3 = pyo.Constraint(rule = Cons3)

def Cons4(model, j):
    return sum(x[1, j] for j in model.j) <= 5000
model.C4 = pyo.Constraint(rule = Cons4)

def Cons5(model, j):
    return sum(x[2, j] for j in model.j) <= 5000
model.C5 = pyo.Constraint(rule = Cons5)

def Cons6(model, j):
    return sum(x[3, j] for j in model.j) <= 5000
model.C6 = pyo.Constraint(rule = Cons6)

def Cons7(model, i):
    return sum(x[i, j] for i in model.i for j in model.j) <= 14e3
model.C7 = pyo.Constraint(rule = Cons7)

def Cons8(model, i):
    return sum(octane[i]*x[i, 1] for i in model.i) / sum(x[i, 1] for i in model.i) >= 10
model.C8 = pyo.Constraint(rule = Cons8)

def Cons9(model, i):
    return sum(octane[i]*x[i, 2] for i in model.i) / sum(x[i, 2] for i in model.i) >= 8
model.C9 = pyo.Constraint(rule = Cons9)

# Redundant
def Cons10(model, i):
    return sum(octane[i]*x[i, 3] for i in model.i) / sum(x[i, 3] for i in model.i) >= 6
model.C10 = pyo.Constraint(rule = Cons10)

def Cons11(model, i):
    return sum(sulphur[i]*x[i, 1] for i in model.i) / sum(x[i, 1] for i in model.i) <= 1
model.C11 = pyo.Constraint(rule = Cons11)

def Cons12(model, i):
    return sum(sulphur[i]*x[i, 2] for i in model.i) / sum(x[i, 2] for i in model.i) <= 2
model.C12 = pyo.Constraint(rule = Cons12)

def Cons13(model, i):
    return sum(sulphur[i]*x[i, 3] for i in model.i) / sum(x[i, 3] for i in model.i) <= 1
model.C13 = pyo.Constraint(rule = Cons13)

# Obj Function

def Obj_Fn(model, i):
    rev = 0
    for j in model.j:
        rev += SP[j]*sum(x[i, j] for i in model.i)
    purc = 0
    for i in model.i:
        purc += PP[i]*sum(x[i, j] for j in model.j)
    adv = sum(a[j] for j in model.j)
    prod = 4*sum(x[i, j] for i in model.i for j in model.j)
    return rev - purc - adv - prod

model.obj = pyo.Objective(rule = Obj_Fn, sense = pyo.maximize)

# model.pprint()

sol = SolverFactory("couenne")
res = sol.solve(model)

for i in model.i:
    for j in model.j:
        print("x", i, j, "=", x[i, j]())
print("The total profit for selling the gasoline is", model.obj())

for j in model.j:
    print("a", j, "=", np.round(a[j]()))

















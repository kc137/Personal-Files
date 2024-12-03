import pyomo.environ as pyo, numpy as np
from pyomo.opt import SolverFactory

model = pyo.ConcreteModel()

# Sets

model.i = pyo.RangeSet(1, 2)
model.j = pyo.Set(initialize = ["A", "B"])

# Vars

model.D = pyo.Var(model.j, domain = pyo.NonNegativeReals)
D = model.D

model.C = pyo.Var(model.i, domain = pyo.NonNegativeReals)
C = model.C

model.X = pyo.Var(model.i, model.j, domain = pyo.NonNegativeReals)
X = model.X

# Constraints

def Cons1(model):
    return X[1, "A"] + X[2, "A"] == D["A"]
model.C1 = pyo.Constraint(rule = Cons1)

def Cons2(model):
    return X[1, "B"] + X[2, "B"] == D["B"]
model.C2 = pyo.Constraint(rule = Cons2)

def Cons3(model):
    return X[1, "A"] + X[1, "B"] <= C[1]
model.C3 = pyo.Constraint(rule = Cons3)

def Cons4(model):
    return X[2, "A"] + X[2, "B"] <= C[2]
model.C4 = pyo.Constraint(rule = Cons4)

def Cons5(model):
    return X[1, "A"] >= 0.7*D["A"]
model.C5 = pyo.Constraint(rule = Cons5)

def Cons6(model):
    return X[2, "B"] >= 0.6*D["B"]
model.C6 = pyo.Constraint(rule = Cons6)

model.C7 = pyo.Constraint(expr = D["A"] <= 40)
model.C8 = pyo.Constraint(expr = D["B"] <= 30)
model.C9 = pyo.Constraint(expr = C[1] <= 45)
model.C10 = pyo.Constraint(expr = C[2] <= 40)

# Obj

def Obj_Fn(model):
    return 6*D["A"] + 5*D["B"] - 6*C[1] - 4*C[2]
model.Obj = pyo.Objective(rule = Obj_Fn, sense = pyo.maximize)
# model.pprint()

sol = SolverFactory("couenne")
res = sol.solve(model)

print("Total profit from selling the drugs =", model.Obj())

for i in model.i:
    print("Chemical purchasing cost of", C[i], "is", C[i]())
    
for j in model.j:
    print("Drug selling cost of", D[j], "is", D[j]())
    
for j in model.j:
    for i in model.i:
        print("Ounces produced of", X[i, j], "will be", X[i, j](), "from chemical", C[i])
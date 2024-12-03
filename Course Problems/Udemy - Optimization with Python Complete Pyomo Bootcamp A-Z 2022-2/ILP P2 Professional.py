import pyomo.environ as pyo, numpy as np
from pyomo.opt import SolverFactory

model = pyo.ConcreteModel()

# Sets

model.i = pyo.RangeSet(1, 2)
model.j = pyo.RangeSet(1, 3)

# Parameters

model.PC = pyo.Param(model.i, initialize = {1 : 1000, 2 : 2000})
PC = model.PC

model.Sal = pyo.Param(model.i, initialize = {1 : 400, 2 : 600})
Sal = model.Sal

model.Seats = pyo.Param(model.i, model.j, initialize = 
                        ({(1, 1) : 20000, (1, 2) : 30000, (1, 3) : 40000, 
                         (2, 1) : 50000, (2, 2) : 35000, (2, 3) : 45000}))
Seats = model.Seats

# Variabes

model.x = pyo.Var(model.i, within = pyo.NonNegativeIntegers)
x = model.x

model.y = pyo.Var(model.i, within = pyo.Binary)
y = model.y

# Constraints

def Constraint1(model, j):
    return sum(Seats[i, 1]*x[i] for i in model.i) >= 120000
model.C1 = pyo.Constraint(model.i, rule = Constraint1)

def Constraint2(model, j):
    return sum(Seats[i, 2]*x[i] for i in model.i) >= 150000
model.C2 = pyo.Constraint(model.i, rule = Constraint2)

def Constraint3(model,  j):
    return sum(Seats[i, 3]*x[i] for i in model.i) >= 200000
model.C3 = pyo.Constraint(model.i, rule = Constraint3)

def Constraint4(model, i):
    return x[i] <= 30*y[i]
model.C4 = pyo.Constraint(model.i, rule = Constraint4)

# Objjective Function

def Obj_Fn(model):
    return sum(PC[i]*y[i] for i in model.i) + sum(Sal[i]*x[i] for i in model.i)

model.Obj = pyo.Objective(rule = Obj_Fn, sense = pyo.minimize)

Sol = SolverFactory("couenne", executable = "F:\\Solvers\\couenne\\bin\\couenne.exe")
Ans = Sol.solve(model)

print("Total Production Cost is", model.Obj())

for i in model.i:
    print("Workers in Production Line", i, "are :", x[i]())
    print("Decision for PL", i, "is", np.round(y[i]()))











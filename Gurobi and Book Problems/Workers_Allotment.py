import pyomo.environ as pyo, numpy as np
from pyomo.opt import SolverFactory

model = pyo.ConcreteModel()

days = {1 : "Monday", 2 : "Tuesday", 3 : "Wednesday", 4 : "Thursday", 5 : "Friday", 6 : "Saturday", 7 : "Sunday"}

# Sets

model.i = pyo.RangeSet(1, 7)

# Vars

model.x = pyo.Var(model.i, domain = pyo.Integers, bounds = (0, 50))
x = model.x

# Constraints

def Cons1(model):
    return sum(x[i] for i in range(1, 6)) >= 14

model.C1 = pyo.Constraint(rule = Cons1)

def Cons2(model):
    return sum(x[i] for i in range(2, 7)) >= 16

model.C2 = pyo.Constraint(rule = Cons2)

def Cons3(model):
    return sum(x[i] for i in range(3, 8)) >= 11

model.C3 = pyo.Constraint(rule = Cons3)

def Cons4(model):
    return x[1] + sum(x[i] for i in range(4, 8)) >= 17

model.C4 = pyo.Constraint(rule = Cons4)

def Cons5(model):
    return x[1] + x[2] + sum(x[i] for i in range(5, 8)) >= 13

model.C5 = pyo.Constraint(rule = Cons5)

def Cons6(model):
    return x[1] + x[2] + x[3] + sum(x[i] for i in range(6, 8)) >= 15

model.C6 = pyo.Constraint(rule = Cons6)

def Cons7(model):
    return x[7] + sum(x[i] for i in range(1, 5)) >= 19

model.C7 = pyo.Constraint(rule = Cons7)

# Obj Function

def Obj_Fn(model, i):
    return sum(x[i] for i in model.i)

model.Obj = pyo.Objective(rule = Obj_Fn, sense = pyo.minimize)

sol = SolverFactory("glpk")
res = sol.solve(model)

model.pprint()
print("Total workers are", model.Obj())
for i in model.i:
    print("Workers that start on", days[i], "are", x[i]())
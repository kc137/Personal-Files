import pyomo.environ as pyo, numpy as np
from pyomo.opt import SolverFactory

model = pyo.ConcreteModel()

# Vars

model.x1 = pyo.Var(within = pyo.NonNegativeReals)
x1 = model.x1

model.x2 = pyo.Var(within = pyo.NonNegativeReals)
x2 = model.x2

# Constraints

def Cons1(model):
    return (1/40)*x1 + (1/60)*x2 <= 1
model.C1 = pyo.Constraint(rule = Cons1)

def Cons2(model):
    return (1/50)*x1 + (1/50)*x2 <= 1
model.C2 = pyo.Constraint(rule = Cons2)

# Obj Function

def Obj_Fn(model):
    return 3e2*x1 + 2e2*x2
model.Obj = pyo.Objective(rule = Obj_Fn, sense = pyo.minimize)

sol = SolverFactory("glpk")
res = sol.solve(model)

print("No. of Trucks manufactured =", x1())
print("Commercial Spots purchased for Football Ads =", x2())
print("Minimized Cost after purchasing of ads is", model.Obj(), "$")
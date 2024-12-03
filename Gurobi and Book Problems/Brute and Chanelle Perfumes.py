import pyomo.environ as pyo, numpy as np
from pyomo.opt import SolverFactory

model = pyo.ConcreteModel()

# Vars

model.RB = pyo.Var(domain = pyo.NonNegativeReals)
rb = model.RB

model.LB = pyo.Var(domain = pyo.NonNegativeReals)
lb = model.LB

model.RC = pyo.Var(domain = pyo.NonNegativeReals)
rc = model.RC

model.LC = pyo.Var(domain = pyo.NonNegativeReals)
lc = model.LC

model.Raw = pyo.Var(domain = pyo.NonNegativeReals)
raw = model.Raw

# Constraints

model.C1 = pyo.Constraint(expr = raw <= 4000)

def Cons2(model):
    return raw + 3*lb + 2*lc <= 6000

model.C2 = pyo.Constraint(rule = Cons2)

def Cons3(model):
    return rb + lb == 3*raw

model.C3 = pyo.Constraint(rule = Cons3)

def Cons4(model):
    return rc + lc == 4*raw

model.C4 = pyo.Constraint(rule = Cons4)

# Obj Function

def Obj_Fn(model):
    return 7*rb + 18*lb + 6*rc + 14*lc - 3*raw - (4*lb + 4*lc)

model.obj = pyo.Objective(rule = Obj_Fn, sense = pyo.maximize)

sol= SolverFactory("couenne")
res = sol.solve(model)

print("Total Regular Brutes Sold -->", np.round(rb(), 2), "oz.")
print("Total Luxury Brutes Sold -->", np.round(lb(), 2), "oz.")
print("Total Regular Chanelles Sold -->", np.round(rc(), 2), "oz.")
print("Total Luxury Chanelles Sold -->", np.round(lc(), 2), "oz.")
print("Total Raw Material Purchased -->", raw(), "pounds")

print("Total profit made by selling regular and luxury perfumes =", model.obj())
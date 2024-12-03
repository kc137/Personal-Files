import pyomo.environ as pyo, numpy as np
from pyomo.opt import SolverFactory

model = pyo.ConcreteModel()

# Vars

model.xr = pyo.Var(within = pyo.NonNegativeIntegers, bounds = (0, 100))
xr = model.xr

model.xt = pyo.Var(within = pyo.NonNegativeIntegers, bounds = (0, 100))
xt = model.xt

# Constraints

model.C1 = pyo.Constraint(expr = 50*xr + 35*xt <= 6000)
model.C2 = pyo.Constraint(expr = 20*xr + 15*xt >= 2000)

# Obj Function

def Obj_Fn(model):
    return 20*xr + 15*xt
model.Obj = pyo.Objective(rule = Obj_Fn, sense = pyo.maximize)

sol = SolverFactory("couenne")
res = sol.solve(model)

print("Total profits made by selling", int(xr()), "Radios and", int(xt()), "Tape Recorders"
      , "is", int(model.Obj()), "$")
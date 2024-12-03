import pyomo.environ as pyo, numpy as np, pandas as pd
from pyomo.opt import SolverFactory

max_investment = 1e5

model= pyo.ConcreteModel()

# Sets

model.i = pyo.RangeSet(1, 5)
model.t = pyo.RangeSet(0, 2)

# Parameters

dat1 = {0 : [-1, 0, -1, -1, 0], 1 : [0.5, -1, 1.2, 0, 0], 2 : [1, 0.5, 0, 0, 1], 
        3 : [0, 1, 0, 1.9, 1.5]}

data = pd.DataFrame(dat1, index = [1, 2, 3, 4, 5])

investments = ["", "A", "B", "C", "D", "E"]

# Variables

model.x = pyo.Var(model.i, within = pyo.NonNegativeReals, bounds = (0, 75e3))
x = model.x

model.s = pyo.Var(model.t, within = pyo.NonNegativeReals)
s = model.s

# Constraints

def Cons1(model, i):
    return max_investment == x[1] + x[3] + x[4] + s[0]
model.C1 = pyo.Constraint(rule = Cons1)

model.C2 = pyo.Constraint(expr = 0.5*x[1] + 1.2*x[3] + 1.08*s[0] == x[2] + s[1])

model.C3 = pyo.Constraint(expr = x[1] + 0.5*x[2] + 1.08*s[1] == x[5] + s[2])

# Obj Function

def Obj_Fn(model, i):
    return sum(data[3][i]*x[i] for i in model.i) + 1.08*s[2]

model.Obj = pyo.Objective(rule = Obj_Fn, sense = pyo.maximize)

sol = SolverFactory("couenne")
res = sol.solve(model)

print("The total returns from investing in 5 investments =", model.Obj())

for i in model.i:
    print("The investment in", investments[i], "=", x[i]())
    
for t in model.t:
    print("The investment in", s[t], "=", s[t]())
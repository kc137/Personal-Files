import pyomo.environ as pyo, pandas as pd
from pyomo.opt import SolverFactory

model = pyo.ConcreteModel()

# Sets

model.i = pyo.RangeSet(1, 9)

y1 = {1 : 12, 2 : 54, 3 : 6, 4 : 6, 5 : 30, 6 : 6, 7 : 48, 8 : 36, 9 : 18}
y2 = {1 : 3, 2 : 7, 3 : 6, 4 : 2, 5 : 35, 6 : 6, 7 : 4, 8 : 3, 9 : 3}
NPV = {1 : 14, 2 : 17, 3 : 17, 4 : 15, 5 : 40, 6 : 12, 7 : 14, 8 : 10, 9 : 12}

data = pd.DataFrame([y1, y2, NPV], index = [1, 2, 3])

# Var

model.x = pyo.Var(model.i, domain = pyo.NonNegativeReals, bounds = (0, 1))
x = model.x

# Constraints

def Cons1(model):
    return sum(data[i][1]*x[i] for i in model.i) <= 50
model.C1 = pyo.Constraint(rule = Cons1)

def Cons2(model):
    return sum(data[i][2]*x[i] for i in model.i) <= 20
model.C2 = pyo.Constraint(rule = Cons2)

# Obj Function

def Obj_Fn(model):
    return sum(data[i][3]*x[i] for i in model.i)
model.Obj = pyo.Objective(rule = Obj_Fn, sense = pyo.maximize)

# Solution

sol = SolverFactory("glpk")
res = sol.solve(model)

for i in model.i:
    print(f"The Company should purchase {round(100*x[i](), 2)} in Project-{i}")
print(f"Total NPV is {round(model.Obj(), 2)}")
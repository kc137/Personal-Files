import pyomo.environ as pyo, numpy as np
from pyomo.opt import SolverFactory

model = pyo.ConcreteModel()

# Vars

model.x1 = pyo.Var(domain = pyo.NonNegativeReals, bounds = (0, None))
x1 = model.x1
model.x2 = pyo.Var(domain = pyo.NonNegativeReals, bounds = (0, None))
x2 = model.x2

# Constraints

def Cons1(model):
    return x1 - x2 == -8
model.C1 = pyo.Constraint(rule = Cons1)

def Cons2(model):
    return 2*x1 + 2*x2 <= 194
model.C2 = pyo.Constraint(rule = Cons2)

# Obj Function

def Obj(model):
    return x1*x2 - 180

model.Obj = pyo.Objective(rule = Obj, sense = pyo.maximize)

solver = SolverFactory("couenne", executable = "F:\\Solvers\\couenne\\bin\\couenne.exe")
res = solver.solve(model)

print("Width =", np.round(x1(), 3), "m")
print("Length =", np.round(x2(), 3), "m")
print("Maximied Area is", np.round(model.Obj(), 3), "sq. m")
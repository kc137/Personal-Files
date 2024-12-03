import pyomo.environ as pyo, numpy as np
from pyomo.opt import SolverFactory

model = pyo.ConcreteModel()

# Vars

model.A = pyo.Var(domain = pyo.NonNegativeReals)
A = model.A
model.B = pyo.Var(domain = pyo.NonNegativeReals)
B = model.B
model.x1 = pyo.Var(domain = pyo.NonNegativeReals)
x1 = model.x1
model.y1 = pyo.Var(domain = pyo.NonNegativeReals)
y1 = model.y1
model.x2 = pyo.Var(domain = pyo.NonNegativeReals)
x2 = model.x2
model.y2 = pyo.Var(domain = pyo.NonNegativeReals)
y2 = model.y2
model.x3 = pyo.Var(domain = pyo.NonNegativeReals)
x3 = model.x3
model.y3 = pyo.Var(domain = pyo.NonNegativeReals)
y3 = model.y3

# , bounds = (0, None)

# Constraints

model.C1 = pyo.Constraint(expr = 6 <= x1)
model.C2 = pyo.Constraint(expr = x1 <= B - 6)
model.C3 = pyo.Constraint(expr = 6 <= y1)
model.C4 = pyo.Constraint(expr = y1 <= A - 6)
model.C5 = pyo.Constraint(expr = 12 <= x2)
model.C6 = pyo.Constraint(expr = x2 <= B - 12)
model.C7 = pyo.Constraint(expr = 12 <= y2)
model.C8 = pyo.Constraint(expr = y2 <= A - 12)
model.C9 = pyo.Constraint(expr = 16 <= x3)
model.C10 = pyo.Constraint(expr = x3 <= B - 16)
model.C11 = pyo.Constraint(expr = y3 >= 16)
model.C12 = pyo.Constraint(expr = y3 <= A - 16)

model.C13 = pyo.Constraint(expr = (x1 - x2)**2 + (y1 - y2)**2 >= 324)
model.C14 = pyo.Constraint(expr = (x1 - x3)**2 + (y1 - y3)**2 >= 484)
model.C15 = pyo.Constraint(expr = (x2 - x3)**2 + (y2 - y3)**2 >= 784)

# Obj Function

model.Obj = pyo.Objective(expr = 2*(A + B), sense = pyo.minimize)

# Solve

Sol = SolverFactory("ipopt", executable = "F:\\Solvers\\ipopt\\bin\\ipopt.exe")
# Sol = SolverFactory("couenne", executable = "F:\\Solvers\\couenne\\bin\\couenne.exe")
res = Sol.solve(model)

print("Co-ordinates (X1, Y1) = (%.3f, %.3f)" %(x1(), y1()))
print("Co-ordinates (X2, Y2) = (%.3f, %.3f)" %(x2(), y2()))
print("Co-ordinates (X3, Y3) = (%.3f, %.3f)" %(x3(), y3()))
print("Optimized Width is", np.round(A(), 3))
print("Optimized Length is", np.round(B(), 3))
print("Minimized area of the box is", np.round(model.Obj(), 3))
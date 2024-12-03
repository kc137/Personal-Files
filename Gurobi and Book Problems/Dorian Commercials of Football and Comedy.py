import pyomo.environ as pyo
from pyomo.opt import SolverFactory

model = pyo.ConcreteModel()

# Sets

# Variables

# model.C = pyo.Var(domain = pyo.NonNegativeIntegers)
model.C = pyo.Var(domain = pyo.NonNegativeReals)
C = model.C

# model.F = pyo.Var(domain = pyo.NonNegativeIntegers)
model.F = pyo.Var(domain = pyo.NonNegativeReals)
F = model.F

# Constraints

model.C1 = pyo.Constraint(expr = 7*C + 2*F >= 28)

model.C2 = pyo.Constraint(expr = 2*C + 12*F >= 24)

# Objective Function

model.Obj = pyo.Objective(expr = 50e3*C + 100e3*F, sense = pyo.minimize)

# Solve

sol = SolverFactory("cplex")
res = sol.solve(model)

print(C(), F(), model.Obj())


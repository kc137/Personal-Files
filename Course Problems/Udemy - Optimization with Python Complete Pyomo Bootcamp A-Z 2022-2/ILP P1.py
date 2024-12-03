import pyomo.environ as pyo
from pyomo.opt import SolverFactory

model = pyo.ConcreteModel()

# Vars

model.x = pyo.Var(range(1, 4), within = pyo.NonNegativeIntegers)
x = model.x

# Constraints

model.C1 = pyo.Constraint(expr = 3*x[1] + 2*x[2] + 6*x[3] <= 150)
model.C2 = pyo.Constraint(expr = 4*x[1] + 3*x[2] + 4*x[3] <= 160)

# Obj Function

model.Obj = pyo.Objective(expr = 6*x[1] + 4*x[2] + 7*x[3], sense = pyo.maximize)

# Solve

sol = SolverFactory("couenne", executable = "F:\\Solvers\\couenne\\bin\\couenne.exe")
res = sol.solve(model)

for i in range(1, 4):
    print("x[", i, "]", "=", x[i]())
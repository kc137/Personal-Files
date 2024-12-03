import pyomo.environ as pyo
from pyomo.opt import SolverFactory

model = pyo.ConcreteModel()

# Vars

model.x1 = pyo.Var(domain = pyo.Integers, bounds = (0, 20))
x1 = model.x1

model.x2 = pyo.Var(domain = pyo.Integers, bounds = (0, 20))
x2 = model.x2

# Objective Function

model.Obj = pyo.Objective(expr = 30*x1 + 35*x2 - 2*(x1**2) - 3*(x2**2), sense = pyo.maximize)

# Constraints

model.C1 = pyo.Constraint(expr = x1 + x2 <= 20)
model.C2 = pyo.Constraint(expr = (x1**2) + 2*(x2**2) <= 250)

# Solver = SolverFactory("mindtpy")
# results = Solver.solve(model, mip_solver = "glpk", nlp_solver = "ipopt")

Solver = SolverFactory("couenne")
results = Solver.solve(model)

print("Total profit be selling the crude oil is", model.Obj())
print("The Crude Oil of type x1 sold is", x1())
print("The Crude Oil of type x2 sold is", x2())
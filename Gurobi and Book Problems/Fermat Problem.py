import pyomo.environ as pyo
from pyomo.opt import SolverFactory

model = pyo.ConcreteModel()

# Variables

model.x = pyo.Var(domain = pyo.NonNegativeReals)
x = model.x
model.y = pyo.Var(domain = pyo.NonNegativeReals)
y = model.y
model.z = pyo.Var(domain = pyo.NonNegativeReals)
z = model.z
model.k = pyo.Var(domain = pyo.NonNegativeReals)
k = model.k

# Constraints

model.C1 = pyo.Constraint(expr = k >= 0)

# Objective Function

model.Obj = pyo.Objective(expr = x**k + y**k - z**k, sense = pyo.minimize)

# Solution

sol = SolverFactory("couenne")
res = sol.solve(model)

print(f"x = {x()}")
print(f"y = {y()}")
print(f"z = {z()}")
print(f"k = {k()}")

print(f"Our objective function is {model.Obj()}")
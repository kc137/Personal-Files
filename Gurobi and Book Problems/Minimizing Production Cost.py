import pyomo.environ as pyo
from pyomo.opt import SolverFactory

model = pyo.ConcreteModel()

demand = 10e3

# Sets

model.M = pyo.Set(initialize = ["A", "B", "C"])

# Variables

model.P = pyo.Var(model.M, domain = pyo.NonNegativeIntegers)
P = model.P

model.C = pyo.Var(model.M, domain = pyo.NonNegativeReals)
C = model.C

# Constraints

model.costs = pyo.ConstraintList()

for m in model.M:
    model.costs.add(C["A"] == 0.1*P["A"]**2 + 0.5*P["A"] + 0.1)
    model.costs.add(C["B"] == 0.3*P["B"] + 0.5)
    model.costs.add(C["C"] == 0.01*P["C"]**3)

model.quantity = pyo.ConstraintList()
model.quantity.add(sum(P[m] for m in model.M) >= 10000)

# Objective Function

def Obj_Fn(model):
    return sum(C[m] for m in model.M)
model.Obj = pyo.Objective(rule = Obj_Fn, sense = pyo.minimize)

# Solution

sol = SolverFactory("couenne")
res = sol.solve(model)

for m in model.M:
    print(f"The quantity produced by Machine-{m} = {P[m]()}")
print(f"Total minimized cost of production = {model.Obj()}")


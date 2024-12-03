import pyomo.environ as pyo, numpy as np
from pyomo.opt import SolverFactory

model = pyo.ConcreteModel()

# Fixed Values
cost, overtime = 400, 450
hold = 20

# Sets

model.i = pyo.RangeSet(1, 4)
model.j = pyo.RangeSet(0, 4)

# Params

model.demand = pyo.Param(model.i, initialize = {1 : 40, 2 : 60, 3 : 75, 4 : 25})
dem = model.demand


# Vars

model.x = pyo.Var(model.i, within = pyo.NonNegativeIntegers, bounds = (0, 40))
x = model.x

model.y = pyo.Var(model.i, within = pyo.NonNegativeIntegers)
y = model.y

model.inv = pyo.Var(model.j, within = pyo.NonNegativeIntegers)
inv = model.inv

# Constraints

model.C1 = pyo.ConstraintList()

for i in model.i:
    if i == 1:
        model.C1.add(inv[1] == 10 + x[1] + y[1] - dem[1])
    else:
        model.C1.add(inv[i] == inv[i-1] + x[i] + y[i] - dem[i])

# Obj Function

def Obj_Fn(model):
    return (cost*sum(x[i] for i in model.i) + overtime*sum(y[i] for i in model.i) + hold*sum(inv[i] for i in model.i))
model.Obj = pyo.Objective(rule = Obj_Fn, sense = pyo.minimize)

model.pprint()

sol = SolverFactory("couenne")
res = sol.solve(model)

for i in model.i:
    print("Ships produced during quarter", i, "will be", x[i]())

for i in model.i:
    print("Ships produced during quarter", i, "(overhead) will be", y[i]())

for j in model.j:
    print("Inventory stored during quarter", j, "is", inv[j]())

print("The total production cost for ships =", model.Obj(), "$")



















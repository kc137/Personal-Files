import pyomo.environ as pyo
from pyomo.opt import SolverFactory

model = pyo.ConcreteModel()

# Sets and Parameters

model.nodes = pyo.RangeSet(1, 6)
model.arcs = pyo.Set(initialize = ["A", "B", "C", "D", "E", "F"])

model.pathsl = pyo.RangeSet(1, 7)
model.paths = pyo.Param(model.pathsl, domain = pyo.Any, 
                        initialize = {1 : (1, 2), 2 : (1, 3), 3 : (3, 4), 4 : (3, 5), 5 : (4, 5), 6 : (5, 6), 7 : (2, 3)})
paths = model.paths

model.days = pyo.Param(model.pathsl, domain = pyo.Any, 
                       initialize = {1 : 9, 2 : 6, 3 : 7, 4 : 8, 5 : 10, 6 : 12, 7 : 0})

# Variables

model.x = pyo.Var(model.nodes, domain = pyo.NonNegativeIntegers, bounds = (0, None))
x = model.x

# Constraints

model.C1lst = pyo.ConstraintList()
for i in model.pathsl:
    model.C1lst.add(x[paths[i][1]] >= x[paths[i][0]] + model.days[i])

model.C2 = pyo.Constraint(expr = x[1] == 0)
    
# Objective Function

def Obj_Fn(model):
    return x[6] - x[1]
model.Obj = pyo.Objective(rule = Obj_Fn, sense = pyo.minimize)

# Solution

sol = SolverFactory("couenne")
res = sol.solve(model)

print(f"The total project time is {model.Obj()}")

for i in model.nodes:
    print(f"{x[i]} = {x[i]()}")
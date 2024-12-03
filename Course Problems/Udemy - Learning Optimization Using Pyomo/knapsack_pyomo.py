import pyomo.environ as pyo
from pyomo.opt import SolverFactory

# Model Declaration
model = pyo.ConcreteModel()

# Sets
model.i = pyo.RangeSet(1, 4)

# Params
w_list = [5, 7, 4, 3]
model.weights = pyo.Param(model.i, within = pyo.Any, initialize = {i : w_list[i-1] for i in range(1, 5)})

v_list = [8, 3, 6, 11]
model.value = pyo.Param(model.i, within = pyo.Any, initialize = {i : v_list[i-1] for i in range(1, 5)})

# Variables
model.x = pyo.Var(model.i, within = pyo.Binary)
x = model.x

# Constraints

def max_weight(model):
    return sum(x[i]*model.weights[i] for i in model.i) <= 14

model.c1 = pyo.Constraint(rule = max_weight)

# Objective Function

def obj_fn(model):
    return sum(x[i]*model.value[i] for i in model.i)

model.obj = pyo.Objective(rule = obj_fn, sense = pyo.maximize)

# Solution

sol = SolverFactory("cplex")
res = sol.solve(model)

print(res)

for i in model.i:
    if x[i]():
        print(f"Weight-{i} is included")
print(f"All give the final solution of {model.obj()}")
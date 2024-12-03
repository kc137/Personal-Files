import pyomo.environ as pyo
from pyomo.opt import SolverFactory

arcs_dict = {}

with open("gritting.txt", "r") as data:
    for line in data:
        f_line = line.replace("(", "")
        f_line = f_line.replace(")", ",")
        f_line = f_line.replace("\n", "")
        nums = f_line.split(", ")
        arcs_dict[(int(nums[0]), int(nums[1]))] = int(nums[2])                

model = pyo.ConcreteModel()

# Sets

model.roads = pyo.RangeSet(1, 12)
model.arcs = pyo.Set(initialize = arcs_dict.keys())

# Parameters

for i in model.roads:
    for j in model.roads:
        if (i, j) not in arcs_dict and i != j:
            arcs_dict[(i, j)] = 0

model.distances = pyo.Param(model.roads, model.roads, 
                            within = pyo.Any, 
                            initialize = arcs_dict)

# Variables

model.x = pyo.Var(model.roads, model.roads, 
                  within = pyo.NonNegativeIntegers)
x = model.x

# Constraints

def continuous_flow(model, i):
    return (sum(x[i, j] for j in model.roads)
            == sum(x[j, i] for j in model.roads))
model.c1 = pyo.Constraint(model.roads, rule = continuous_flow)

def total_arcs(model, i, j):
    if (i, j) in model.arcs:
        return x[i, j] >= 1
    else:
        return x[i, j] == 0
model.c2 = pyo.Constraint(model.roads, model.roads, rule = total_arcs)

# Objective Function

def obj_fn(model):
    return sum(x[i, j]*model.distances[i, j] for i, j in model.arcs 
               if i != j)
model.obj = pyo.Objective(rule = obj_fn, sense = pyo.minimize)

# Solution

sol = SolverFactory("cplex")
res = sol.solve(model)

print(res)

res_dict_out = {n : 0 for n in model.roads}
res_dict_in = {n : 0 for n in model.roads}

for i in model.roads:
    for j in model.roads:
        if x[i, j]():
            print(f"{x[i, j]} = {x[i, j]()}")
            res_dict_out[i] += x[i, j]()
            res_dict_in[j] += x[i, j]()
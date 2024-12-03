import pyomo.environ as pyo
from pyomo.opt import SolverFactory

model = pyo.ConcreteModel()
C = 100

weights_list = [34, 6, 8, 17, 16, 5, 13, 21, 25, 31, 14, 13, 33, 9, 25, 25]

# Sets and Parameters

model.boxes = pyo.RangeSet(1, 16)
model.wagons = pyo.RangeSet(1, 3)

model.weights = pyo.Param(model.boxes, within = pyo.Any, 
                          initialize = {
                              w : weights_list[w-1] for w in model.boxes
                              })
weights = model.weights

# Variables

model.box_dist = pyo.Var(model.boxes, model.wagons, within = pyo.Binary)
box_dist = model.box_dist

model.max_weight = pyo.Var(within = pyo.NonNegativeReals, bounds = (0, None))
max_weight = model.max_weight

# Constratints

def wagon_max_cap(model, b):
    return sum(box_dist[b, w]*weights[b] for w in model.wagons) <= max_weight
model.c1 = pyo.Constraint(model.boxes, rule = wagon_max_cap)

def wagon_cap(model, w):
    return sum(box_dist[b, w]*weights[b] for b in model.boxes) <= max_weight
model.c2 = pyo.Constraint(model.wagons, rule = wagon_cap)

def box_once(model, b):
    return sum(box_dist[b, w] for w in model.wagons) == 1
model.c3 = pyo.Constraint(model.boxes, rule = box_once)

# Objective Function

def obj_fn(model):
    return max_weight
model.obj = pyo.Objective(rule = obj_fn, sense = pyo.minimize)

# Solution

sol = SolverFactory("cplex")
res = sol.solve(model)

print(res)

weights_dict = {w : 0 for w in model.wagons}

for b in model.boxes:
    for w in model.wagons:
        if box_dist[b, w]():
            print(f"{box_dist[b, w]} = {box_dist[b, w]()}")
        weights_dict[w] += box_dist[b, w]()*weights[b]
    
for w in model.wagons:
    print(f"Weight in Wagon-{w} : {weights_dict[w]} quintals")
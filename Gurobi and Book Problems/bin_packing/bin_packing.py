import pyomo.environ as pyo
from pyomo.opt import SolverFactory

# Model

model = pyo.ConcreteModel()

# Sets and Parameters

max_w = 9
w = [2,3,4,5,6,7,8]
q = [4,2,6,6,2,2,2]
weights=[]
for j in range(len(w)):
    for i in range(q[j]):
        weights.append(w[j])

print(weights)

model.items_ = pyo.RangeSet(1, len(weights))
items = model.items_

model.b = pyo.RangeSet(1, len(weights))
bins = model.b

# Variables

model.x = pyo.Var(items, bins, within = pyo.Binary)
x = model.x

model.y = pyo.Var(bins, within = pyo.Binary)
y = model.y

# Constraints

def max_weight(model, j):
    return pyo.quicksum(x[i, j]*weights[i-1] for i in items) <= max_w*y[j]
model.c1 = pyo.Constraint(bins, rule = max_weight)

def item_once(model, i):
    return pyo.quicksum(x[i, j] for j in bins) == 1
model.c2 = pyo.Constraint(items, rule = item_once)

# Objective Function

def obj_fn(model):
    return pyo.quicksum(y[j] for j in bins)
model.obj = pyo.Objective(rule = obj_fn, sense = pyo.minimize)

# Solution

sol = SolverFactory("cplex")
res = sol.solve(model)

# Printing the Solution

print(f"Total bins used : {pyo.quicksum(y[j]() for j in bins)}")

bin_dist = {b : [] for b in bins}

for i in items:
    for b in bins:
        if x[i, b]() and x[i, b]() >= 0.9:
            bin_dist[b].append(weights[i-1])

print(bin_dist)

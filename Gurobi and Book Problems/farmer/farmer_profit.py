import pyomo.environ as pyo
from pyomo.opt import SolverFactory

model = pyo.ConcreteModel()

# Sets and Parameters

model.crops = pyo.RangeSet(1, 3)
model.ppy = pyo.RangeSet(1, 2)
model.spw = pyo.RangeSet(1, 4)

yields = [2.5, 3, 20]
planting_cost = [150, 230, 260]
sp = [170, 150, 36, 10]
pp = [238, 210]
min_req = [200, 240]

# Variables

model.x = pyo.Var(model.crops, within = pyo.NonNegativeReals)
x = model.x

model.y = pyo.Var(model.ppy, within = pyo.NonNegativeReals)
y = model.y

model.w = pyo.Var(model.spw, within = pyo.NonNegativeReals)
w = model.w

# Constraints

def acres(model):
    return pyo.quicksum(x[c] for c in model.crops) <= 500
model.c2 = pyo.Constraint(rule = acres)

def wheat_corn(model, sy):
    return yields[sy-1]*x[sy] + y[sy] - w[sy] >= min_req[sy-1]
model.c1 = pyo.Constraint(model.ppy, rule = wheat_corn)

model.sugar_cons = pyo.ConstraintList()

model.sugar_cons.add(w[3] + w[4] <= 20*x[3])
model.sugar_cons.add(w[3] <= 6000)

# Objective Function

def obj_fn(model):
    return (pyo.quicksum(w[i]*sp[i-1] - y[i]*pp[i-1] 
                        for i in model.ppy) - 
            pyo.quicksum(x[yi]*planting_cost[yi-1] 
                         for yi in model.crops) + 
            36*w[3] + 10*w[4])
model.obj = pyo.Objective(rule = obj_fn, sense = pyo.maximize)

# Solution

sol = SolverFactory("cplex")
res = sol.solve(model)

# Printing the Solution

for c in model.crops:
    print(f"The land for Crop-{c} : {x[c]()} acres.")

print(f"The Profit for this year for the Farmer is : {model.obj()} $.")

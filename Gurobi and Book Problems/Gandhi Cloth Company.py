import pyomo.environ as pyo
from pyomo.opt import SolverFactory

model = pyo.ConcreteModel()

# Sets and Parameters

model.i = pyo.RangeSet(1, 3)
model.q = pyo.Set(initialize = ["Shirts", "Shorts", "Pants"])
profits = [6, 4, 7]
mc_cost = [200, 150, 100]
max_hours = 150
max_cloth = 160
hrs_req = [3, 2, 6]
cloth_req = [4, 3, 4]

# Variables

model.x = pyo.Var(model.i, domain = pyo.NonNegativeIntegers)
x = model.x

model.y = pyo.Var(model.i, domain = pyo.Binary)
y = model.y

# Constraints

def Labour(model):
    return sum(x[i]*hrs_req[i-1] for i in model.i) <= max_hours
model.labour_cons = pyo.Constraint(rule = Labour)

def Cloth(model):
    return sum(x[i]*cloth_req[i-1] for i in model.i) <= max_cloth
model.cloth_cons = pyo.Constraint(rule = Cloth)

model.bin_cons = pyo.ConstraintList()

for i in model.i:
    model.bin_cons.add(x[i] <= y[i]*100)

# Objective Function

def Obj_Fn(model):
    return sum(x[i]*profits[i-1] - y[i]*mc_cost[i-1] for i in model.i)
model.Obj = pyo.Objective(rule = Obj_Fn, sense = pyo.maximize)

# Solution

sol = SolverFactory("cplex")
res = sol.solve(model)

# Printing the Solution

for i in model.i:
    if x[i]():
        print(f"The number of {model.q.at(i)} manufactured : {round(x[i]())} units.")
        # print(f"The number of {model.q[i]} manufactured : {x[i]()} units.")
    else:
        print(f"No {model.q.at(i)} were produced.")

print(f"The weekly profits of Gandhi Cloth Company : {round(model.Obj())} $")
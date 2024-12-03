import pyomo.environ as pyo, pandas as pd
from pyomo.opt import SolverFactory

model = pyo.ConcreteModel()

# Sets and Parameters

model.i = pyo.RangeSet(1, 4)
model.j = pyo.RangeSet(1, 4)

dat1 = {1 : [2, 6, 8, 8], 2 : [6, 2, 5, 5], 3 : [8, 5, 2, 5], 4 : [8, 5, 5, 2]}
data = pd.DataFrame(dat1, index = [1, 2, 3, 4])

regions = {1 : "West", 2 : "Mid-West", 3 : "East", 4 : "South"}
cities = {1 : "LA", 2 : "Chicago", 3 : "NY", 4 : "Atlanta"}

costs = {1 : 70e3, 2 : 50e3, 3 : 60e3, 4 : 40e3}

annual_cost = 50e3

# Variables

# If region-i sends payment to city-j
model.x = pyo.Var(model.i, model.j, domain = pyo.Binary)
x = model.x

# If a lockbox is operated in city-j
model.y = pyo.Var(model.j, domain = pyo.Binary)
y = model.y

# Constraints

def Cons1(model, i):
    return sum(x[i, j] for j in model.j) == 1
model.C1 = pyo.Constraint(model.i, rule = Cons1)

def Cons2(model, i, j):
    return x[i, j] <= y[j]
model.C2 = pyo.Constraint(model.i, model.j, rule = Cons2)

# Objective Function

def Obj_Fn(model):
    return (sum(0.2*x[i, j]*costs[i]*data[j][i] for i in model.i for j in model.j) + 
            sum(y[j]*annual_cost for j in model.j))
model.Obj = pyo.Objective(rule = Obj_Fn, sense = pyo.minimize)

# Solution

sol = SolverFactory("glpk")
res = sol.solve(model)

for j in model.j:
    if y[j]():
        print(f"\n1 lockbox is in {cities[j]}")

for i in model.i:
    for j in model.j:
        if x[i, j]():
            print(f"\nMoney is sent from {regions[i]} to {cities[j]}")

print(f"\nMinimized lost interest is {model.Obj()}")

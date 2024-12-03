import pyomo.environ as pyo, json, pandas as pd
from pyomo.opt import SolverFactory

costs = {}

with open("input_transp.json") as data:
    data = json.load(data)
    availabilities = data["availabilities"]
    demands = data["demands"]
    costs_dict = data["costs"]
    for cost in costs_dict:
        costs[cost["from"], cost["to"]] = cost["value"]
    availabilities["S2"] = 23

# Model

model = pyo.ConcreteModel()

# Sets

model.S = pyo.Set(initialize = availabilities.keys())
model.D = pyo.Set(initialize = demands.keys())

# Variables

model.x = pyo.Var(model.S, model.D, within = pyo.NonNegativeReals)
x = model.x

model.z = pyo.Var(model.D, within = pyo.NonNegativeReals)
z = model.z

# Constraints

def supply_cons(model, i):
    return pyo.quicksum(x[i, :]) <= availabilities[i]
model.c1 = pyo.Constraint(model.S, rule = supply_cons)

def demand_cons(model, j):
    return pyo.quicksum(x[:, j]) + z[j] == demands[j]
model.c2 = pyo.Constraint(model.D, rule = demand_cons)

# Objective Function

def obj_fn_balance(model):
    return pyo.quicksum(z[:])
model.obj_balance = pyo.Objective(rule = obj_fn_balance)

def obj_fn_cost(model):
    return pyo.quicksum(x[i, j]*costs[i, j] 
                        for i in model.S 
                        for j in model.D)
model.obj_cost = pyo.Objective(rule = obj_fn_cost, sense = pyo.minimize)

model.obj_cost.deactivate()

# Solution_1

sol = SolverFactory("cplex")
res = sol.solve(model)

# Printing the Solution

print(res)

K = model.obj_balance()

def balance_constraint(model):
    return pyo.quicksum(z[:]) <= K
model.c3 = pyo.Constraint(rule = balance_constraint)

model.obj_balance.deactivate()
model.obj_cost.activate()

# Solution_2

sol = SolverFactory("cplex")
res = sol.solve(model)

print(res)

sol = [
       {"from" : i, "to" : j, "value" : val}
       for (i, j), val in x.extract_values().items()
       ]

df = pd.DataFrame(sol).pivot(index = "from", columns = "to", values = "value")

print(df)





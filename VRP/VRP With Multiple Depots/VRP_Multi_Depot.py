import pyomo.environ as pyo, pandas as pd
from pyomo.opt import SolverFactory
from collections import defaultdict

model = pyo.ConcreteModel()

D = 2
N = 11
VeD1, VeD2 = 2, 2
max_dist = 160

# M = 1000 # Not needed now as there is no penalty involved.

# Sets and Parameters

model.D = pyo.Set(initialize = ["D" + str(i) for i in range(1, D+1)])
model.N = pyo.Set(initialize = ["D" + str(i) for i in range(1, D+1)] + ["C" + str(i) for i in range(1, N-D+1)])
model.C = pyo.Set(initialize = ["C" + str(i) for i in range(1, N-D+1)])
model.V = pyo.Set(initialize = ["V"+str(i)+"D1" for i in range(1, VeD1+1)] + ["V"+str(i)+"D2" for i in range(1, VeD1+1)])
model.VD1 = pyo.Set(initialize = ["V"+str(i)+"D1" for i in range(1, VeD1+1)])
model.VD2 = pyo.Set(initialize = ["V"+str(i)+"D2" for i in range(1, VeD2+1)])

disdata = pd.read_excel("VRP_Multi_Depot_Data.xlsx", header = 0, index_col = 0, usecols = "A:L", nrows = 11)

demdata = pd.read_excel("VRP_Multi_Depot_Data.xlsx", header = 13, index_col = 0, usecols = "A:L", nrows = 2)

vcap = pd.read_excel("VRP_Multi_Depot_Data.xlsx", header = 16, index_col = 0, usecols = "A:E", nrows = 2)

dem_dict = {}
for d in model.D:
    dem_dict[d] = 0
for cust in model.C:
    dem_dict[cust] = demdata[cust]["Demands"]
model.demand = pyo.Param(model.N, domain = pyo.Any, initialize = dem_dict)

dist = defaultdict(int)

for Ve in model.V:
    dist[Ve] = 0

# Variables

model.x = pyo.Var(model.N, model.N, model.V, domain = pyo.Binary)
x = model.x
model.u = pyo.Var(model.N, domain = pyo.NonNegativeReals)
u = model.u

# Constraints

model.enter_cons = pyo.ConstraintList()
for i in model.N:
    for j in model.C:
        if i == "D1":
            model.enter_cons.add(sum(x[i, j, k] for k in model.VD1 for i in model.N) <= 1)
        elif i == "D2":
            model.enter_cons.add(sum(x[i, j, k] for k in model.VD2 for i in model.N) <= 1)
        else:
            model.enter_cons.add(sum(x[i, j, k] for k in model.V for i in model.N) <= 1)

def Flow(model, j, k):
    return sum(x[i, j, k] for i in model.N if i != j) == sum(x[j, i, k] for i in model.N)
model.flow_cons = pyo.Constraint(model.N, model.V, rule = Flow)

model.depot_1 = pyo.ConstraintList()
for k in model.VD1:
    model.depot_1.add(sum(x["D1", j, k] for j in model.C) <= 1)
    model.depot_1.add(sum(x[i, "D1", k] for i in model.C) <= 1)
    model.depot_1.add(sum(x["D2", j, k] for j in model.C) == 0)

model.depot_2 = pyo.ConstraintList()
for k in model.VD2:
    model.depot_2.add(sum(model.x["D2", j, k] for j in model.C) <= 1)
    model.depot_2.add(sum(model.x[i, "D2", k] for i in model.C) <= 1)
    model.depot_2.add(sum(x["D1", j, k] for j in model.C) == 0)

def Capacity(model, k):
    return sum(x[i, j, k]*model.demand[j] 
               for i in model.N for j in model.C) <= vcap[k]["Capacity"]
model.capacity_cons = pyo.Constraint(model.V, rule = Capacity)

def Distance(model, k):
    return sum(x[i, j, k]*disdata[j][i] 
               for i in model.N for j in model.C) <= max_dist
model.distance_cons = pyo.Constraint(model.V, rule = Distance)

def Subtour(model, i, j, k):
    if i != j:
        return model.u[i] - model.u[j] + N*(model.x[i, j, k]) <= N-1
    else:
        return model.u[i] - model.u[i] == 0
model.sub_tour = pyo.Constraint(model.C, model.C, model.V, rule = Subtour)

model.subtour = pyo.ConstraintList()

for k in model.V:
    for i in model.C:
        model.subtour.add(model.demand[i] <= model.u[i])
        model.subtour.add(vcap[k]["Capacity"] >= model.u[i])

model.total_routes = pyo.ConstraintList()

model.total_routes.add(sum(x[i, j, k] for k in model.V for i in model.N for j in model.N if i != j) 
                       == (N-2)+VeD1+1)

def Obj_Fn(model):
    return sum(x[i, j, k]*disdata[j][i] for k in model.V for i in model.N 
               for j in model.N if i != j)
model.Obj = pyo.Objective(rule = Obj_Fn, sense = pyo.minimize)

# Solution

sol = SolverFactory("cplex")
res = sol.solve(model)

for k in model.V:
    for i in model.N:
        for j in model.N:
            if model.x[i, j, k]():
                print(f"{model.x[i, j, k]} = {model.x[i, j, k]()}")

total_load = 0
for k in model.V:
    tload = 0
    print(f'Route for vehicle-{k}:')
    route = [f"{i} to {j} -> {model.demand[j]}" for i in model.N
              for j in model.N
              if (x[i, j, k]() and x[i, j, k].value >= 0.9) if i != j]
    for i in model.N:
        for j in model.N:
            if model.x[i, j, k]() and model.x[i, j, k]() >= 0.9:
                dist[k] += disdata[j][i]
                tload += model.demand[j]
    total_load += tload
    print(route if route else "Vehicle remained at Depot.")
    print(f"\nVehicle-{k} travelled {dist[k]} m with a total load of {tload} tons\n")
print(f"Total load after all routes = {total_load} tons")





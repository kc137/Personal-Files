import pyomo.environ as pyo, pandas as pd, matplotlib.pyplot as plt, math
from pyomo.opt import SolverFactory

# Model

model = pyo.ConcreteModel()

N = 16
V = 4
Vcap = [100, 100, 100, 100]


# Sets

model.N = pyo.Set(initialize = ["D"] + ["C" + str(i) for i in range(1, N)])
model.C = pyo.Set(initialize = ["C" + str(i) for i in range(1, N)])
model.V = pyo.Set(initialize = ["V" + str(i) for i in range(1, V+1)])

# Params

model.coords = pd.read_excel("CVRP_16_16.xlsx", sheet_name = "Coords", index_col = 0, header = 0, nrows = 16, usecols = "A:C")
coords = model.coords

# Eucl_Distance
distance = {k : [] for k in model.N}
for P1 in model.N:
    for P2 in model.N:
        if P1 == P2:
            distance[P1].append(0)
        else:
            distance[P1].append(round(math.hypot(
                (coords["x"][P1] - coords["x"][P2]), (coords["y"][P1] - coords["y"][P2]))))
            
distance_network = pd.DataFrame(distance, index = model.N)

model.demand = pd.read_excel("CVRP_16_16.xlsx", sheet_name = "Demand", index_col = 0, header = 0, nrows = 16, usecols = "A:B")
demand = model.demand

vehicle_capacity = {model.V.at(i+1) : Vcap[i] for i in range(V)}

model.VC = pyo.Param(model.V, domain = pyo.Any, initialize = vehicle_capacity)

# Variables

model.x = pyo.Var(model.N, model.N, model.V, domain= pyo.Binary)
x = model.x
model.u = pyo.Var(model.N, domain = pyo.NonNegativeReals)
u = model.u

# Constraints

model.Once = pyo.ConstraintList()
for j in model.C:
    model.Once.add(sum(x[i, j, k] for i in model.N for k in model.V) == 1)

model.Depot = pyo.ConstraintList()
for k in model.V:
    model.Depot.add(sum(x["D", j, k] for j in model.C) == 1)

for k in model.V:
    model.Depot.add(sum(x[i, "D", k] for i in model.C) == 1)

model.Flow = pyo.ConstraintList()
for k in model.V:
    for j in model.N:
        model.Flow.add(
            sum(x[i, j, k] for i in model.N if i != j) == 
            sum(x[j, i, k] for i in model.N))

def Capacity(model, k):
    return sum(x[i, j, k]*demand["Demand"][j] 
               for i in model.N 
               for j in model.C if i != j) <= model.VC[k]
model.capacity = pyo.Constraint(model.V, rule = Capacity)

model.subtour = pyo.ConstraintList()

for k in model.V:
    for i in model.C:
        for j in model.C:
            model.subtour.add(
                u[j] - u[i] >= demand["Demand"][j] - model.VC[k]*(1 - x[i, j, k]))

# Objective Function

def Obj_Fn(model):
    return sum(x[i, j, k]*distance_network[j][i] if i != j else 0
               for k in model.V
               for i in model.N
               for j in model.N)
model.Obj = pyo.Objective(rule = Obj_Fn)

# Solution

sol = SolverFactory("cplex")
res = sol.solve(model, timelimit = 10)

for k in model.V:
    route = []
    tload = 0
    vdist = 0
    for i in model.N:
        for j in model.N:
            if x[i, j, k]() and x[i, j, k]() >= 0.9:
                route.append(f"{(i, j)}-({demand['Demand'][j]}, {distance_network[j][i]})")
                tload += demand['Demand'][j]
                vdist += distance_network[j][i]
    print(f"\nVehicle-{k} travelled a distance of {vdist} km with a load of {tload} Tons")
    print(f"\n{route}")
    


print(f"\nTotal distance Travelled = {model.Obj()}")










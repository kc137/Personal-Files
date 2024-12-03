# import random, matplotlib.pyplot as plt

# locations = {i : [] for i in range(1, 5)}

# x = [random.randint(100, 200) for _ in range(4)]
# y = [random.randint(100, 200) for _ in range(4)]

# plt.scatter(x, y)

import pyomo.environ as pyo, matplotlib.pyplot as plt, networkx as nx, numpy as np, pandas as pd, math
from pyomo.opt import SolverFactory

depot_color = "red"
colors = ["darkviolet", "limegreen", "darkorange", "magenta", "darkturquoise"]

model = pyo.ConcreteModel()

N = 17
V = 4

# Sets and Parameters

model.N = pyo.Set(initialize = ["D"] + ["C" + str(i) for i in range(1, N)])

model.C = pyo.Set(initialize = ["C" + str(i) for i in range(1, N)])

model.V = pyo.Set(initialize = ["V" + str(i) for i in range(1, V+1)])

coords_list = [(0, 0), (139, 120), (164, 167), (105, 155), (113, 185), 
               (-166, 143), (-176, 128), (-105, 160), (-105, 101), 
              (-180, -139), (-101, -150), (-189, -173), (-193, -110), 
              (188, -110), (167, -189), (113, -111), (127, -179)]

coords_list = [(0, 0), 
 (167, -189),
 (-193, -110),
 (105, 155),
 (188, -110),
 (113, 185),
 (-176, 128),
 (-105, 160),
 (-180, -139),
 (164, 167),
 (127, -179),
 (139, 120),
 (-101, -150),
 (-105, 101),
 (-166, 143),
 (113, -111),
 (-189, -173)]

coords = pd.DataFrame(coords_list, columns = ["x", "y"], index = [l for l in model.N])

distances = {n : [] for n in model.N}

# Euclidean Distance Calculation

for p1 in model.N:
    for p2 in model.N:
        if p1 != p2:
            distances[p1].append(round(math.hypot(
                coords["x"][p1] - coords["x"][p2], coords["y"][p1] - coords["y"][p2])))
        else:
            distances[p1].append(0)

distance_network = pd.DataFrame(distances, index = [l for l in model.N])

# Demand and Capacity DataFrames

capacities = [100 for _ in range(V)]

capacity_df = pd.DataFrame(capacities, index = model.V, columns = ["Capacity"])

demands = [0, 15, 25, 34, 25, 20, 28, 17, 33, 25, 22, 19, 27, 20, 16, 21, 20]

demands_df = pd.DataFrame(demands, index = [n for n in model.N], columns = ["Demand"])

# Variables

# Binary Decision Variable to decide a route from i to j by a vehice k
model.x = pyo.Var(model.N, model.N, model.V, domain = pyo.Binary)
x = model.x

# Subtour elimination variable
model.u = pyo.Var(model.N, domain = pyo.NonNegativeReals)
u = model.u

# Constraints

def Once(model, j):
    return sum(x[i, j, k] for k in model.V for i in model.N if i != j) == 1
model.once_cons = pyo.Constraint(model.C, rule = Once)

def Flow(model, k, j):
    return sum(x[i, j, k] for i in model.N if i != j) == sum(x[j, i, k] for i in model.N if i != j)
model.flow_cons = pyo.Constraint(model.V, model.C, rule = Flow)

def Capacity(model, k):
    return sum(x[i, j, k]*demands_df["Demand"][j] 
               for i in model.N 
               for j in model.C if i != j) <= capacity_df["Capacity"][k]
model.capacity_cons = pyo.Constraint(model.V, rule = Capacity)

def Depot(model, k):
    return sum(x["D", j, k] for j in model.C) == 1
model.depot_cons = pyo.Constraint(model.V, rule = Depot)

model.subtour_cons = pyo.ConstraintList()
for k in model.V:
    for i in model.C:
        for j in model.C:
            if i != j:
                model.subtour_cons.add(
                    u[j] - u[i] >= (demands_df["Demand"][j] - 
                                    capacity_df["Capacity"][k]*(1 - x[i, j, k])))

# Objective Function

def Obj_Fn(model):
    return sum(x[i, j, k]*distance_network[j][i] 
               for k in model.V 
               for i in model.N 
               for j in model.N if i != j)
model.Obj = pyo.Objective(rule = Obj_Fn)

# Solution

sol = SolverFactory("cplex")
res = sol.solve(model)
sol.options["mipgap"] = 0.1

print(f"Total Distance : {model.Obj()}")

paths = {v : [] for v in model.V}

for k in model.V:
    for i in model.N:
        for j in model.N:
            if x[i, j, k]() and round(x[i, j, k]()) == 1:
                paths[k].append((i, j))
    print(f"Path of Vehicle-{k} : ")
    print(paths[k])

# # Solution Plot

# G = nx.DiGraph()

# vehicle_colors = {v : c for v, c in zip(model.V, colors)}

# edges = paths.copy()
# nodes = {v : [] for v in model.V}
# for v in model.V:
#     for edge in edges[v]:
#         if edge[0] != model.N.at(1):
#             nodes[v].append(edge[0])

# node_colors_dict = {model.N.at(1) : depot_color}
# for v in model.V:
#     for node in nodes:
#         node_colors_dict[node] = vehicle_colors[v]

# node_colors = []
# for n in model.N:
#     node_colors.append(node_colors_dict[n])
    
# city_positions_list = coords_list.copy()




















import pyomo.environ as pyo, pandas as pd, networkx as nx
from pyomo.environ import Constraint
from pyomo.opt import SolverFactory

model = pyo.ConcreteModel()

# Sets and Parameters

model.i = pyo.RangeSet(1, 5)
model.j = pyo.RangeSet(1, 5)

model.ii = pyo.RangeSet(2, 5)
model.jj = pyo.RangeSet(2, 5)

C = pd.read_excel("S5P3_Data.xlsx", sheet_name = "TSP", header = 0, index_col = 0, usecols = "A:F", nrows = 5)
data = pd.DataFrame(C)
N = len(data)

# Variables

model.x = pyo.Var(model.i, model.j, domain = pyo.Binary)
x = model.x

model.u = pyo.Var(model.i, domain = pyo.NonNegativeReals)
u = model.u

# Constraints

def Cons1(model, i):
    return sum(x[i, j] for j in model.j) == 1
model.C1 = pyo.Constraint(model.i, rule = Cons1)

def Cons2(model, j):
    return sum(x[i, j] for i in model.i) == 1
model.C2 = pyo.Constraint(model.j, rule = Cons2)

def Cons3(model, i, j):
    if i != j:
        return u[i] - u[j] + N*x[i, j] <= N - 1
    else:
        return u[i] == u[i]
        # return u[i] - u[i] == 0
model.C3 = pyo.Constraint(model.ii, model.jj, rule = Cons3)

# Objective Function

def Obj_Fn(model):
    return sum(x[i, j]*C[j][i] for i in model.i for j in model.j)
model.Obj = pyo.Objective(rule = Obj_Fn, sense = pyo.minimize)

# Solution

sol = SolverFactory("cbc")
res = sol.solve(model)

print(f"Total distance to travel for salesman is {model.Obj()} km")

paths = []

for i in model.i:
    for j in model.j:
        if round(x[i, j]()):
            paths.append((i, j))
            
# fromp = {key : 0 for key in model.i}
# for p in paths:
#     fromp[p[0]] += p[1]

# travel = [1]

# while len(travel) < len(paths):
#     curr = travel[-1]
#     travel.append(fromp[travel[-1]])
    
# print("\nPath of the salesman will be :\n")

# print(f"{travel[0]}", end = " ")

# for c in range(1, len(travel)):
#     print(f"--> {travel[c]}", end = " ")
# print(f"--> {travel[0]}", end = "")

nodes = [i for i in range(1, 6)]

G = nx.DiGraph()
G.add_nodes_from(nodes)
G.add_edges_from(paths)
nx.draw_circular(G, with_labels = True, node_size = 500, edge_color = "r", node_color = "b", arrowsize = 10)














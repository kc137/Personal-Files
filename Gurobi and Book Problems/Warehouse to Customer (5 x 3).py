import networkx as nx
import pyomo.environ as pyo, pandas as pd
from pyomo.opt import SolverFactory

model = pyo.ConcreteModel()

# Sets and Parameters

model.i = pyo.RangeSet(1, 3)
model.j = pyo.RangeSet(1, 5)

demands = {1 : 80, 2 : 270, 3 : 250, 4 : 160, 5 : 180}
maxsup = {1 : 500, 2 : 500, 3 : 500} # Max Supply

dat1 = {1 : [4, 5, 6, 8, 10], 2 : [6, 4, 3, 5, 8], 3 : [9, 7, 4, 3, 4]}
data = pd.DataFrame(dat1, index = [1, 2, 3, 4, 5]).transpose()

# Variables

model.d = pyo.Var(model.i, model.j, domain = pyo.NonNegativeIntegers)
d = model.d

model.xj = pyo.Var(model.i, domain = pyo.Binary)
xj = model.xj

# Constraints

def Cons1(model, j):
    return sum(d[i, j] for i in model.i) == demands[j]
model.C1 = pyo.Constraint(model.j, rule = Cons1)

def Cons2(model, i):
    return sum(d[i, j] for j in model.j) <= maxsup[i]*xj[i]
model.C2 = pyo.Constraint(model.i, rule = Cons2)

def Cons3(model, i, j):
    return (d[i, j]) <= demands[j]*xj[i]
model.C3 = pyo.Constraint(model.i, model.j, rule = Cons3)

# Objective Function

def Obj_Fn(model):
    return (sum(d[i, j]*data[j][i] for i in model.i for j in model.j) + 
            sum(xj[i]*1000 for i in model.i))
model.Obj = pyo.Objective(rule = Obj_Fn, sense = pyo.minimize)

# Solution

sol = SolverFactory("glpk")
res = sol.solve(model)

nodes1 = [i for i in range(11, 14)]
nodes2 = [i for i in range(1, 6)]
edges = []

for i in model.i:
    for j in model.j:
        print(f"Supply from Warehouse-{i} to Customer-{j} is {d[i, j]()} Units.")
        if d[i, j]():
            edges.append((i, j))
        
print(f"Total cost of transportation will be {model.Obj()} $.")

G = nx.DiGraph()
G.add_nodes_from(nodes1)
G.add_nodes_from(nodes2)
G.add_edges_from(edges)
nx.draw(G, with_labels = True, node_size = 500, node_color = "y", edge_color = "b", arrowsize = 10)
import pyomo.environ as pyo, networkx as nx
from pyomo.opt import SolverFactory

# Data

edges = []

arcs = []
caps = []
pos = []

with open("max_flow_networkx.dat") as data:
    lines = data.read().splitlines()
    
    for line in lines[2:22]:
        curr = line.replace("PIPE: ", "").replace("[", "").replace("]", "")
        curr = curr.split()
        arcs.append((int(curr[-2]), int(curr[-1])))
    
    cap_line = lines[23]
    cap_line = cap_line.replace("CAP: ", "").replace("[(1)", "").replace("]", "")
    cap_line = cap_line.split()
    for cap in cap_line:
        caps.append(int(cap))
    
    for line in lines[28:]:
        curr = line.replace("POS: ", "").replace("[", "").replace("]", "")
        curr = curr.split()
        pos.append((int(curr[0]), int(curr[1])))
    
for arc, cap in zip(arcs, caps):
    edges.append(((arc[0], arc[1]), cap))
    
G = nx.DiGraph()

for arc, cap in edges:
    G.add_edge(arc[0], arc[1], capacity = cap)

for n in range(1, 13):
    G.add_node(n, pos = pos[n-1])

# Model

model = pyo.ConcreteModel()

# Sets and Params

model.cities = pyo.RangeSet(1, 12)
cities = model.cities

# Variables

model.flow = pyo.Var(arcs, within = pyo.NonNegativeReals)
flow = model.flow

# Constraints

def flow_cap(model, u, v):
    return flow[u, v] <= G[u][v]["capacity"]
model.c1 = pyo.Constraint(arcs, rule = flow_cap)

def flow_continuity(model, node):
    if node not in [11, 12]:
        return (pyo.quicksum(flow[u, v] for u, v in G.in_edges(node)) 
                == pyo.quicksum(flow[u, v] for u, v in G.out_edges(node)))
    else:
        return pyo.Constraint.Skip
model.c2 = pyo.Constraint(cities, rule = flow_continuity)

# def supply_cons(model):
#     return pyo.quicksum(flow[11, v] for v in G.successors(11)) <= 60
# model.c3 = pyo.Constraint(rule = supply_cons)

# Objective Function

def obj_fn(model):
    return pyo.quicksum(flow[11, v] for v in G.successors(11))
model.obj = pyo.Objective(rule = obj_fn, sense = pyo.maximize)

# Solution

sol = SolverFactory("cplex")
res = sol.solve(model)

# Printing the Solution

print(res)





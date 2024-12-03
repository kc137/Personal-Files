import pyomo.environ as pyo, networkx as nx
from pyomo.opt import SolverFactory

# Model

model = pyo.ConcreteModel()

# Sets and Params

edges = [
    ("A", "B", {"d" : 10, "c" : 100, "w" : 5}), 
    ("A", "C", {"d" : 20, "c" : 50, "w" : 4}), 
    ("B", "C", {"d" : 5, "c" : 50, "w" : 3}), 
    ("B", "D", {"d" : 10, "c" : 100, "w" : 8}), 
    ("C", "Z", {"d" : 30, "c" : 100, "w" : 2}), 
    ("D", "Z", {"d" : 20, "c" : 50, "w" : 6}), 
    ]

graph = nx.DiGraph()

for u, v, att in edges:
    graph.add_edge(u, v, capacity = att["c"], weight = att["w"])

# Variables

model.flow = pyo.Var(graph.edges(), within = pyo.NonNegativeReals)
flow = model.flow

# Constraints

def flow_cap(model, u, v):
    return flow[u, v] <= graph[u][v]["capacity"]
model.c1 = pyo.Constraint(graph.edges(), rule = flow_cap)

def flow_continuity(model, node):
    if node not in ["A", "Z"]:
        return (pyo.quicksum(flow[u, v] for u, v in graph.in_edges(node)) 
                == pyo.quicksum(flow[u, v] for u, v in graph.out_edges(node)))
    else:
        return pyo.Constraint.Skip
model.c2 = pyo.Constraint(graph.nodes(), rule = flow_continuity)

def supply(model):
    return pyo.quicksum(flow["A", v] for v in graph.successors("A")) == 150
model.c3 = pyo.Constraint(rule = supply)

def demand(model):
    return pyo.quicksum(flow[u, "Z"] for u in graph.predecessors("Z")) == 150
model.c4 = pyo.Constraint(rule = demand)

# Objective Function

def obj_fn(model):
    return pyo.quicksum(flow[u, v]*graph[u][v]["weight"] 
                        for u, v in graph.edges())
model.obj = pyo.Objective(rule = obj_fn, sense = pyo.minimize)

# Solution

sol = SolverFactory("cplex")
res = sol.solve(model)

# Printing the Solution

print(res)
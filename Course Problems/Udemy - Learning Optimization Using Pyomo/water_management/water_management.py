import pyomo.environ as pyo
from pyomo.opt import SolverFactory

# Creating Model

model = pyo.ConcreteModel()

with open("water_management.txt", "r") as data:
    arcs = data.read().splitlines()
    arcs = [arc.split() for arc in arcs]
    arcs_list = [(int(arc[0]), int(arc[1])) for arc in arcs]
    capacities_list = [int(arc[2]) for arc in arcs]

# Sets and Parameters

# model.source = pyo.Set(initialize = [11])
# model.sink = pyo.Set(initialize = [12])

model.all_nodes = pyo.RangeSet(1, 12)
model.nodes = pyo.RangeSet(1, 10)

model.arcs = pyo.Set(initialize = arcs_list)

model.capacities = pyo.Param(model.arcs, within = pyo.Any, 
                             initialize = {
                                 arcs_list[i] : capacities_list[i] 
                                 for i in range(len(model.arcs))
                                 })
capacities = model.capacities

model.from_n_to_n = {
    n : [] for n in model.all_nodes
    }

model.to_n_from_n = {
    n : [] for n in model.all_nodes
    }

for node in model.all_nodes:
    for arc in model.arcs:
        if node == arc[0]:
            model.from_n_to_n[node].append(arc[1])
        if node == arc[1]:
            model.to_n_from_n[node].append(arc[0])

# Variables

model.flow = pyo.Var(model.arcs, within = pyo.NonNegativeIntegers)
flow = model.flow

# Constraints

def capacity_cons(model, i, j):
    return flow[i, j] <= capacities[i, j]
model.c1 = pyo.Constraint(model.arcs, rule = capacity_cons)

def flow_cons(model, node):
    return (sum(flow[node, to_n] for to_n in model.from_n_to_n[node]) 
            <= sum(flow[from_n, node] for from_n in model.to_n_from_n[node]))
model.c2 = pyo.Constraint(model.nodes, rule = flow_cons)

# Objective Function

def obj_fn(model):
    goal = model.all_nodes.get(12)
    return sum(flow[city, goal] for city in model.to_n_from_n[goal])
model.obj = pyo.Objective(rule = obj_fn, sense = pyo.maximize)

# Solution

sol = SolverFactory("cplex")
res = sol.solve(model)

print(res)

for arc in model.arcs:
    print(f"{flow[arc]} = {flow[arc]()}")
    
print(f"\nMaximum water flow from source to sink while satisfying the demands of all the cities : {model.obj()} m3/hr")
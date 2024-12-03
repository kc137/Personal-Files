import pyomo.environ as pyo, gurobipy as gp
from pyomo.opt import SolverFactory

supply = dict({'Liverpool': 150000,
               'Brighton': 200000})

through = dict({'Newcastle': 70000,
                'Birmingham': 50000,
                'London': 100000,
                'Exeter': 40000})

demand = dict({'C1': 50000,
               'C2': 10000,
               'C3': 40000,
               'C4': 35000,
               'C5': 60000,
               'C6': 20000})

# Create a dictionary to capture shipping costs.

arcs, cost = gp.multidict({
    ('Liverpool', 'Newcastle'): 0.5,
    ('Liverpool', 'Birmingham'): 0.5,
    ('Liverpool', 'London'): 1.0,
    ('Liverpool', 'Exeter'): 0.2,
    ('Liverpool', 'C1'): 1.0,
    ('Liverpool', 'C3'): 1.5,
    ('Liverpool', 'C4'): 2.0,
    ('Liverpool', 'C6'): 1.0,
    ('Brighton', 'Birmingham'): 0.3,
    ('Brighton', 'London'): 0.5,
    ('Brighton', 'Exeter'): 0.2,
    ('Brighton', 'C1'): 2.0,
    ('Newcastle', 'C2'): 1.5,
    ('Newcastle', 'C3'): 0.5,
    ('Newcastle', 'C5'): 1.5,
    ('Newcastle', 'C6'): 1.0,
    ('Birmingham', 'C1'): 1.0,
    ('Birmingham', 'C2'): 0.5,
    ('Birmingham', 'C3'): 0.5,
    ('Birmingham', 'C4'): 1.0,
    ('Birmingham', 'C5'): 0.5,
    ('London', 'C2'): 1.5,
    ('London', 'C3'): 2.0,
    ('London', 'C5'): 0.5,
    ('London', 'C6'): 1.5,
    ('Exeter', 'C3'): 0.2,
    ('Exeter', 'C4'): 1.5,
    ('Exeter', 'C5'): 0.5,
    ('Exeter', 'C6'): 1.5
})

# Model

model = pyo.ConcreteModel()

# Variables

model.flow = pyo.Var(arcs, within = pyo.NonNegativeReals)
flow = model.flow

# Constraints

def factory_output(model, f):
    return pyo.quicksum(flow[f, d] for f1, d in arcs if f1 == f) <= supply[f]
model.c1 = pyo.Constraint(supply, rule = factory_output)

def customer_demand(model, c):
    return pyo.quicksum(flow[s, c] for s, c1 in arcs if c1 == c) == demand[c]
model.c2 = pyo.Constraint(demand, rule = customer_demand)

def depot_flow(model, d):
    return (pyo.quicksum(flow[s, d] 
                         for s, d1 in arcs if d1 == d) 
            == pyo.quicksum(flow[d, t] 
                            for d1, t in arcs if d1 == d))
model.c3 = pyo.Constraint(through, rule = depot_flow)

def depot_capacity(model, d):
    return pyo.quicksum(flow[s, d] 
                        for s, d1 in arcs if d1 == d) <= through[d]
model.c4 = pyo.Constraint(through, rule = depot_capacity)

# Objective Function

def obj_fn(model):
    return pyo.quicksum(flow[s, d]*cost[s, d] 
                        for s, d in arcs)
model.obj = pyo.Objective(rule = obj_fn, sense = pyo.minimize)

# Solution

sol = SolverFactory("cplex")
res = sol.solve(model)

# Printing the Solution

print(res)

for s, c in arcs:
    if flow[s, c]():
        print(f"Supply of {flow[s, c]()}-units from {s} to {c}")









import pyomo.environ as pyo
from pyomo.opt import SolverFactory
from min_flow_1_data import arcs, arcs_cap, costs, min_q

# Model

model = pyo.ConcreteModel()

# Sets and Params

# Variables

model.flow = pyo.Var(arcs, within = pyo.NonNegativeReals)
flow = model.flow

# Constraints

def flow_bounds(model, i, j):
    return (arcs_cap[(i, j)][0], flow[i, j], arcs_cap[(i, j)][1])
model.c1 = pyo.Constraint(arcs, rule  = flow_bounds)

def min_flow(model):
    return pyo.quicksum(flow[1, j] 
                        for i, j in arcs 
                        if i == 1) == min_q
model.c2 = pyo.Constraint(rule = min_flow)

def flow_maintain(model, i):
    return (pyo.quicksum(flow[i, j] 
                        for i1, j in arcs if i1 == i) 
            == pyo.quicksum(flow[j, i] 
                                for j, i1 in arcs if i1 == i))
model.c3 = pyo.Constraint(list(range(2, 14)), rule = flow_maintain)

# Objective Function

def obj_fn(model):
    return pyo.quicksum(flow[i, j]*costs[i, j] 
                        for i, j in arcs)
model.obj = pyo.Objective(rule = obj_fn, sense = pyo.minimize)

# Solution

sol = SolverFactory("cplex")
res = sol.solve(model)

# Printing the Solution

print(res)
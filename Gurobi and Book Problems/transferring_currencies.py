import pyomo.environ as pyo
from pyomo.opt import SolverFactory

# Model

model = pyo.ConcreteModel()

# Data

supply = [2.4, 0, 0, 350]
demand = [0, 2.5, 5, 0]

exahange = [
    [1, 1.6152, 1.006, 0.02297], 
    [0.6188, 1, 0.62230, 0.01422], 
    [0.9935, 1.6054, 1, 0.02282], 
    [43.522, 70.2967, 43.7831, 1]
    ]

# Sets

model.currencies = pyo.RangeSet(1, 4)
currencies = model.currencies

arcs = [(c1, c2) 
        for c1 in currencies 
        for c2 in currencies 
        if c1 != c2]

# Variables

model.x = pyo.Var(arcs, within = pyo.NonNegativeReals)
x = model.x

# Constraints

def incoming_usd(model):
    return (pyo.quicksum(x[c1, 1]*exahange[0][c1-1] for c1 in currencies if c1 != 1) 
            - pyo.quicksum(x[1, c2] for c2 in currencies if c2 != 1)) >= 5
model.c1 = pyo.Constraint(rule = incoming_usd)

def incoming_gbp(model):
    return (pyo.quicksum(x[c1, 2]*exahange[1][c1-1] for c1 in currencies if c1 != 2) 
            - pyo.quicksum(x[2, c2] for c2 in currencies if c2 != 2)) >= 2.1
model.c2 = pyo.Constraint(rule = incoming_gbp)

def outgoing_eur(model):
    return (-pyo.quicksum(x[c1, 3]*exahange[2][c1-1] for c1 in currencies if c1 != 3) 
            + pyo.quicksum(x[3, c2] for c2 in currencies if c2 != 3)) <= 2.4
model.c3 = pyo.Constraint(rule = outgoing_eur)

def outgoing_inr(model):
    return (-pyo.quicksum(x[c1, 4]*exahange[3][c1-1] for c1 in currencies if c1 != 4) 
            + pyo.quicksum(x[4, c2] for c2 in currencies if c2 != 4)) <= 350
model.c4 = pyo.Constraint(rule = outgoing_inr)

# Objective Function

def obj_fn(model):
    return (pyo.quicksum(x[c1, 1]*exahange[0][c1-1] for c1 in currencies if c1 != 1) 
            - pyo.quicksum(x[1, c2] for c2 in currencies if c2 != 1))
model.obj = pyo.Objective(rule = obj_fn, sense = pyo.maximize)

# Solution

sol = SolverFactory("cplex", solver_io = "python")
res = sol.solve(model)

# Printing the Solution
print(res)
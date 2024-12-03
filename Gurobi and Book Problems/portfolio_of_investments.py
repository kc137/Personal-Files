import pyomo.environ as pyo
from pyomo.opt import SolverFactory

# Model

model = pyo.ConcreteModel()

# Data

fin_req = [20000, 22000, 24000, 26000]

profits = {"A" : 1.05, 
           "B" : 1.13, 
           "C" : 1.28, 
           "D" : 1.40}

# Sets

model.years = pyo.RangeSet(1, 6)
years = model.years

model.choices = pyo.Set(initialize = ["A", "B", "C", "D"])
choices = model.choices

arcs = [(y, c) 
        for y in years 
        for c in choices 
        if (c == "A" and y <= 5)
        or (c == "B" and y <= 4) 
        or (c == "C" and y <= 3) 
        or (c == "D" and y <= 2)]

# Variables

# model.x = pyo.Var(arcs, within = pyo.NonNegativeIntegers)
model.x = pyo.Var(arcs, within = pyo.NonNegativeReals)
x = model.x

model.balance = pyo.ConstraintList()

model.balance.add(1.05*x[1, "A"] - x[2, "A"] - x[2, "B"] - x[2, "C"] - x[2, "D"] == 0)
model.balance.add(1.13*x[1, "B"] + 1.05*x[2, "A"] - x[3, "A"] - x[3, "B"] - x[3, "C"] == fin_req[0])
model.balance.add(1.28*x[1, "C"] + 1.13*x[2, "B"] + 1.05*x[3, "A"] - x[4, "A"] - x[4, "B"] == fin_req[1])
model.balance.add(1.4*x[1, "D"] + 1.28*x[2, "C"] + 1.13*x[3, "B"] + 1.05*x[4, "A"] - x[5, "A"] == fin_req[2])
model.balance.add(1.4*x[2, "D"] + 1.28*x[3, "C"] + 1.13*x[4, "B"] + 1.05*x[5, "A"] == fin_req[2])

model.risk_cons = pyo.ConstraintList()

model.risk_cons.add(x[1, "C"] + x[1, "D"] <= 0.2*(x[1, "A"] + x[1, "B"] + x[1, "C"] + x[1, "D"]))
model.risk_cons.add(0.8*(x[1, "C"] + x[1, "D"] + x[2, "C"] + x[2, "D"]) 
                    <= 0.2*(x[1, "B"] + x[2, "A"] + x[2, "B"]))
model.risk_cons.add(0.8*(x[1, "C"] + x[1, "D"] + x[2, "C"] + x[2, "D"] + x[3, "C"] )
                    <= 0.2*(x[2, "B"] + x[3, "A"] + x[3, "B"]))
model.risk_cons.add(0.8*(x[1, "D"] + x[2, "C"] + x[2, "D"] + x[3, "C"] )
                    <= 0.2*(x[3, "B"] + x[4, "A"] + x[4, "B"]))
model.risk_cons.add(0.8*(x[2, "D"] + x[3, "C"]) <= 0.2*(x[4, "B"] + x[5, "A"]))

# Objective Function

def obj_fn(model):
    return pyo.quicksum(x[1, c] for c in choices)
model.obj = pyo.Objective(rule = obj_fn)

# Solution

sol = SolverFactory("cplex", solver_io = "python")
res = sol.solve(model)

# Printing the Solution

print(res)

for c in choices:
    print(f"Investment made for type-{c} : {x[1, c]()}$")


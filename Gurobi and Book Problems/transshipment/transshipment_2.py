import pyomo.environ as pyo, pandas as pd
from pyomo.opt import SolverFactory

M = 2000

# Model

model = pyo.ConcreteModel()

# Sets and Parameters

model.r = pyo.RangeSet(1, 6)
model.c = pyo.RangeSet(1, 5)

# table = [[10, 13, 25, 28, 0], 
#           [15, 12, 26, 25, 0], 
#           [0, 6, 16, 17, 0], 
#           [6, 0, 14, 16, 0], 
#           [M, M, 0, 15, 0], 
#           [M, M, 15, 0, 0]]

table = [[10, 13, 25, 28, 0], 
          [15, 12, 26, 25, 0], 
          [0, 6, 6, 7, 0], 
          [6, 0, 4, 6, 0], 
          [M, M, 0, 15, 0], 
          [M, M, 15, 0, 0]]

demands = [350e3, 350e3, 490e3, 510e3, 50e3]
supplies = [150e3, 200e3, 350e3, 350e3, 350e3, 350e3]

# Variables

model.x = pyo.Var(model.r, model.c, within = pyo.NonNegativeIntegers)
x = model.x

# Constraints

def supply_cons(model, r):
    return pyo.quicksum(x[r, c] for c in model.c) <= supplies[r-1]
model.c1 = pyo.Constraint(model.r, rule = supply_cons)

def demand_cons(model, c):
    return pyo.quicksum(x[r, c] for r in model.r) >= demands[c-1]
model.c2 = pyo.Constraint(model.c, rule = demand_cons)

# Objective Function

def obj_fn(model):
    return pyo.quicksum(x[r, c]*table[r-1][c-1] 
                        for r in model.r 
                        for c in model.c)
model.obj = pyo.Objective(rule = obj_fn, sense = pyo.minimize)

# Solution

sol = SolverFactory("cplex")
res = sol.solve(model)

# Printing the Solution

res_table = [[0 for _ in range(len(model.c))] for _ in range(len(model.r))]

for r in model.r:
    for c in model.c:
        res_table[r-1][c-1] = x[r, c]()

print(res_table)

print(f"The total transshipment cost for Sunco Oil : {model.obj()}")

"""
[[150000.0, -0.0, -0.0, -0.0, -0.0], 
 [-0.0, 150000.0, -0.0, -0.0, 50000.0], 
 [200000.0, -0.0, -0.0, 150000.0, -0.0], 
 [-0.0, 200000.0, 140000.0, 10000.0, -0.0], 
 [-0.0, -0.0, 350000.0, -0.0, -0.0], 
 [-0.0, -0.0, -0.0, 350000.0, -0.0]]
"""

prev_df = pd.read_excel("results.xlsx", index_col = 0)

cities = ["Well-1", "Well-2", "Mobile", "Galveston", "N.Y.", "L.A."]

df = pd.DataFrame({cities[i] : res_table[i] for i in range(len(cities))}, index = cities[2:] + ["Dummy"]).transpose()

# combined_df = prev_df.join(df)

# combined_df.to_excel("results.xlsx", sheet_name = "Output", startrow = 0)


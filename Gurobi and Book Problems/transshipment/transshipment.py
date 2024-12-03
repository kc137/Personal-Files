import pyomo.environ as pyo
from pyomo.opt import SolverFactory

model = pyo.ConcreteModel()

M = 2000

# Sets and Params

model.i = pyo.RangeSet(1, 2)
model.j = pyo.RangeSet(1, 3)

table = [[4, 6, 10], [2, 7, 8]]

# table = [
#     [M, 140, 100, 90, 225, 0], 
#     [145, M, 111, 110, 119, 0], 
#     [105, 115, M, 113, 78, 0], 
#     [89, 109, 121, M, M, 0], 
#     [210, 117, 82, M, M, 0]
#     ]

demand_col = [10, 30, 20]
supply_row = [30, 30]

# Variables

model.q = pyo.Var(model.i, model.j, within = pyo.NonNegativeReals)
q = model.q

# Constraints

def supply_cons(model, i):
    return pyo.quicksum(q[i, j] for j in model.j) == supply_row[i-1]
model.c1 = pyo.Constraint(model.i, rule = supply_cons)

def demand_cons(model, j):
    return pyo.quicksum(q[i, j] for i in model.i) == demand_col[j-1]
model.c2 = pyo.Constraint(model.j, rule = demand_cons)

# Objective Function

def obj_fn(model):
    return pyo.quicksum(
        q[i, j]*table[i-1][j-1] 
        for i in model.i 
        for j in model.j
        )
model.obj = pyo.Objective(rule = obj_fn, sense = pyo.minimize)

# Solution

sol = SolverFactory("cplex")
res = sol.solve(model)

# Printing the Solution

res_table = [[0 for _ in range(len(model.j))] for _ in range(len(model.i))]

for i in model.i:
    for j in model.j:
        res_table[i-1][j-1] = q[i, j]() if q[i, j]() else 0.0

print(f"The total cost of transshipment : {model.obj()} $.")

"""
      LA  Det  Atl   Hou    Tmp  Dummy
LA  [0.0, 0.0, 0.0, 1100.0, 0.0, 0.0],
Det [0.0, 0.0, 1500.0, 1300.0, 0.0, 100.0],
Atl [0.0, 2500.0, 0.0, 0.0, 1500.0, 0.0],
Hou [4000.0, 0.0, 0.0, 0.0, 0.0, 0.0],
Tmp [0.0, 1500.0, 2500.0, 0.0, 0.0, 0.0]]
    
    [[0.0, 0.0, 0.0, 5100.0, 0.0, 0.0],
     [0.0, 0.0, 4000.0, 1300.0, 1500.0, 100.0],
     [0.0, 0.0, 0.0, 0.0, 4000.0, 0.0],
     [4000.0, 0.0, 0.0, 0.0, 0.0, 0.0],
     [0.0, 4000.0, 0.0, 0.0, 0.0, 0.0]]
    
    [[1100.0, 0.0, 0.0, 0.0, 0.0, 0.0],
     [0.0, 2900.0, 0.0, 0.0, 0.0, 0.0],
     [1300.0, 0.0, 2700.0, 0.0, 0.0, 0.0],
     [1600.0, 0.0, 0.0, 2400.0, 0.0, 0.0],
     [0.0, 1100.0, 1300.0, 0.0, 1500.0, 100.0]]
    
    [[0.0, 0.0, 0.0, 1100.0, 0.0, 0.0],
     [0.0, 0.0, 1500.0, 1300.0, 0.0, 100.0],
     [0.0, 2500.0, 0.0, 0.0, 1500.0, 0.0],
     [4000.0, 0.0, 0.0, 0.0, 0.0, 0.0],
     [0.0, 1500.0, 2500.0, 0.0, 0.0, 0.0]]
"""
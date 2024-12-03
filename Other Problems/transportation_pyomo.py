import pyomo.environ as pyo
from pyomo.opt import SolverFactory

model = pyo.ConcreteModel()

M = 2000

# Sets and Params

model.i = pyo.RangeSet(1, 3)
model.j = pyo.RangeSet(1, 4)

# table = [[3, 1, 7, 4], [2, 6, 5, 9], [8, 3, 3, 2]]

# demand_col = [250, 350, 400, 200]
# supply_row = [300, 400, 500]


table = [[8, 10, 6, 3], [9, 15, 8, 6], [5, 12, 5, 7]]

demand_col = [45, 15, 40, 50]
supply_row = [50, 50, 50]

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

print(f"The total cost of transportation : {model.obj()} $.")

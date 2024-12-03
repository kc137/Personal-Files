import pyomo.environ as pyo, math, numpy as np
from pyomo.opt import SolverFactory

# Model

model = pyo.ConcreteModel()

# Data

N = 10

REQ = "10  6  8 11  9  7 15  7  9 12"
REQ = [int(n) for n in REQ.split()]

STOCK = " 8 13  4  8 12  2 14 11 15  7"
STOCK = [int(n) for n in STOCK.split()]

X = "0 20 18 30 35 33  5  5 11  2"
X = [int(n) for n in X.split()]

Y = "0 20 10 12  0 25 27 10  0 15"
Y = [int(n) for n in Y.split()]

COST = 0.5 # Dollars

EXCESS, NEEDED = [], []

for i in range(N):
    if REQ[i] - STOCK[i] > 0:
        NEEDED.append(i+1)
    else:
        EXCESS.append(i+1)

dist_matrix = [[0]*len(Y) for _ in range(len(X))]

for i in range(N):
    for j in range(N):
        if i != j:
            dist_matrix[i][j] = (1.3*math.hypot(X[i] - X[j], Y[i] - Y[j]))

# Sets

model.N = pyo.RangeSet(1, 10)

# Variables

model.move = pyo.Var(model.N, model.N, within = pyo.NonNegativeIntegers)
move = model.move

# Constraints

def move_excess(model, a):
    return pyo.quicksum(move[a, b] for b in NEEDED) == STOCK[a-1] - REQ[a-1]
model.c1 = pyo.Constraint(EXCESS, rule = move_excess)

def move_needed(model, b):
    return pyo.quicksum(move[a, b] for a in EXCESS) == REQ[b-1] - STOCK[b-1]
model.c2 = pyo.Constraint(NEEDED, rule = move_needed)

# Objective Function

def obj_fn(model):
    return pyo.quicksum(COST*move[a, b]*dist_matrix[a-1][b-1] 
                        for a in EXCESS 
                        for b in NEEDED)
model.obj = pyo.Objective(rule = obj_fn, sense = pyo.minimize)

# Solution

sol = SolverFactory("cplex")
res = sol.solve(model)

# Printing the Solution

print(res)

for c1 in EXCESS:
    for c2 in NEEDED:
        print(f"move{[c1, c2]} = {move[c1, c2]()}")
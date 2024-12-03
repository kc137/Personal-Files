import pyomo.environ as pyo, math
from pyomo.opt import SolverFactory

# x_coords = [5, 34, 17, 37, 37, 31, 42, 40, 45, 43, 50, 49]
# y_coords = [45, 35, 35, 31, 19, 17, 13, 9, 9, 4, 3, 8]

x_coords = [5, 35, 17, 37, 26, 33, 24, 25, 30, 31, 37, 44]
y_coords = [45, 35, 35, 31, 26, 19, 21, 11, 2, 12, 6, 8]

coords = list(zip(x_coords, y_coords))

red = [1, 3, 5, 7, 9, 11]
blue = [2, 4, 6, 8, 10, 12]
N = 12

distance_matrix = [[0]*N for _ in range(N)]

for i in range(N):
    for j in range(N):
        if i != j:
            distance_matrix[i][j] = math.hypot(coords[i][0] - coords[j][0], 
                                               coords[i][1] - coords[j][1])

# Model

model = pyo.ConcreteModel()

# Sets and Params

model.N = pyo.RangeSet(1, N)
model.C = pyo.RangeSet(2, N)
model.red = pyo.Set(initialize = red)
model.blue = pyo.Set(initialize = blue)

# Variables

model.x = pyo.Var(model.N, model.N, within = pyo.Binary)
x = model.x

model.u = pyo.Var(model.N, within = pyo.NonNegativeReals)
u = model.u

# Constraints

def row_once(model, j):
    return pyo.quicksum(x[i, j] 
                        for i in model.N 
                        if i != j) == 1
model.c1 = pyo.Constraint(model.N, rule = row_once)

def col_once(model, i):
    return pyo.quicksum(x[i, j] 
                        for j in model.N 
                        if i != j) == 1
model.c2 = pyo.Constraint(model.N, rule = col_once)

def red_cons(model, r):
    return pyo.quicksum(x[r, ri] 
                        for ri in model.red 
                        if r != ri) == 0
model.c3 = pyo.Constraint(model.red, rule = red_cons)

def blue_cons(model, b):
    return pyo.quicksum(x[b, bi] 
                        for bi in model.blue 
                        if b != bi) == 0
model.c4 = pyo.Constraint(model.blue, rule = blue_cons)

model.sub_tour = pyo.ConstraintList()

for i in model.C:
    for j in model.C:
        if i != j:
            model.sub_tour.add(
                u[i] - u[j] + N*(x[i, j]) <= (N-1)
                )
            
# Objective Function

def obj_fn(model):
    return pyo.quicksum(x[i, j]*distance_matrix[i-1][j-1] 
                        for i in model.N 
                        for j in model.N 
                        if i != j)
model.obj = pyo.Objective(rule = obj_fn, sense = pyo.minimize)

# Solution

sol = SolverFactory("cplex")
res = sol.solve(model)

# Printing the Solution

print(res)

for i in model.N:
    for j in model.N:
        if i != j:
            if x[i, j]() and x[i, j]() >= 0.9:
                print(f"x[{i}, {j}] = {x[i, j]()}")








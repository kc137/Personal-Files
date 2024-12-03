import pyomo.environ as pyo
from pyomo.opt import SolverFactory
from flight_tour_data import DIST, N

# Model

model = pyo.ConcreteModel()

# Sets and Params

model.airports = pyo.RangeSet(1, 7)
airports = model.airports

model.c = pyo.RangeSet(2, 7)
c = model.c

# Variables

model.x = pyo.Var(airports, airports, within = pyo.Binary)
x = model.x

model.u = pyo.Var(airports, within = pyo.NonNegativeReals)
u = model.u

# Constraints

def row_once(model, j):
    return pyo.quicksum(x[i, j] 
                        for i in airports 
                        if i != j) == 1
model.c1 = pyo.Constraint(airports, rule = row_once)

def col_once(model, i):
    return pyo.quicksum(x[i, j] 
                        for j in airports 
                        if i != j) == 1
model.c2 = pyo.Constraint(airports, rule = col_once)

model.sub_tour = pyo.ConstraintList()

for i in c:
    for j in c:
        if i != j:
            # model.sub_tour.add(
            #     u[i] - u[j] + N*(x[i, j]) <= N-1
            #     )
            model.sub_tour.add(
                u[i] - u[j] <= N*(1 - x[i, j]) - 1
                )

# def total_tours(model):
#     return pyo.quicksum(x[i, j] 
#                         for i in airports 
#                         for j in airports 
#                         if i != j) == N
# model.c3 = pyo.Constraint(rule = total_tours)

# Objective Function

def obj_fn(model):
    return pyo.quicksum(x[i, j]*DIST[i-1][j-1] 
                        for i in airports 
                        for j in airports 
                        if i != j)
model.obj = pyo.Objective(rule = obj_fn, sense = pyo.minimize)

# Solution

sol = SolverFactory("cplex")
res = sol.solve(model)

# Printing the Solution

print(res)

s = x.extract_values()

s = {(i, j) : s[i, j] 
     for i, j in s 
     if s[i, j]}
print(s)
if s:
    print(True)


arcs = []

for i in airports:
    for j in airports:
        if x[i, j]() and x[i, j]() >= 0.9:
            arcs.append((i, j))

print(arcs)


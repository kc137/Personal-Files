import pyomo.environ as pyo
from pyomo.opt import SolverFactory
from flight_tour_data import DIST, N

# Define the function for getting subtours

def get_subtours(sol):
    subtours = []
    N = len(sol)
    remaining_nodes = [1 for _ in range(N)]
    left = N
    while left > 0:
        subtour = []
        subtours.append(subtour)
        for i in range(N):
            if remaining_nodes[i]:
                start = i+1
                break
        
        while True:
            
            subtour.append(start)
            if remaining_nodes[start - 1]:
                remaining_nodes[start - 1] = 0
                left -= 1
            
            next_node = next((j for (i, j) in sol if i == start and sol[i, j] >= 0.9))
            
            if not next_node or not remaining_nodes[next_node - 1]:
                break
            
            start = next_node
            
    return subtours

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

# for i in c:
#     for j in c:
#         if i != j:
#             # model.sub_tour.add(
#             #     u[i] - u[j] + N*(x[i, j]) <= N-1
#             #     )
#             model.sub_tour.add(
#                 u[i] - u[j] <= N*(1 - x[i, j]) - 1
#                 )

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

# Procedure for subtour constraints

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

while True:
    sol = SolverFactory("cplex")
    res = sol.solve(model)
    
    s = x.extract_values()
    sol_dict = {(i, j) : s[i, j] 
         for i, j in s 
         if s[i, j] and s[i, j] >= 0.9}
    
    if not sol_dict:
        print("No solution found.")
        break
    
    subtours = get_subtours(sol_dict)
    print(f"Subtours are : {subtours}")
    
    if len(subtours) > 1:
        for subtour in subtours:
            LS = len(subtour)
            if LS < N:
                model.sub_tour.add(
                    pyo.quicksum(x[i, j] 
                                 for i in subtour 
                                 for j in subtour 
                                 if i != j) <= LS - 1
                    )
    else:
        break

# Printing the Solution

print(res)
print(f"Tour : {subtours}")

    
    

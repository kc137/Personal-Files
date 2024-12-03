import pyomo.environ as pyo, math, random, time
from pyomo.opt import SolverFactory
from itertools import permutations

# Model

model = pyo.ConcreteModel()

# BigM

M = 100000

N = 17
locations = [*range(1, N+1)]

K = 5
vehicles = [*range(1, K+1)]

points = [(0, 0)]
points += [(random.randint(0, 50), random.randint(0, 50)) for _ in range(N-1)]

times = {(i, j) : math.hypot(points[i-1][0] - points[j-1][0], 
                            points[i-1][1], points[j-1][1]) 
        for i in locations 
        for j in locations 
        }

# Sets and Params

model.N = pyo.RangeSet(1, N)
model.C = pyo.RangeSet(2, N)
model.K = pyo.RangeSet(1, K)

# Variables

model.x = pyo.Var(model.N, model.N, model.K, within = pyo.Binary)
x = model.x

# Constraints

def once(model, j):
    return pyo.quicksum(x[i, j, k] 
                        for i in model.N 
                        for k in model.K 
                        if i != j) == 1
model.c1 = pyo.Constraint(model.C, rule = once)

def flow(model, j, k):
    return (pyo.quicksum(x[i, j, k] for i in model.N if i != j) 
            == pyo.quicksum(x[j, i, k] for i in model.N if i != j))
model.c2 = pyo.Constraint(model.C, model.K, rule = flow)

def depot(model, k):
    return pyo.quicksum(x[1, j, k] 
                        for j in model.C) == 1
model.c3 = pyo.Constraint(model.K, rule = depot)

def capacity(model, k):
    return pyo.quicksum(x[i, j, k]*times[i, j] 
                        for i in model.N 
                        for j in model.C 
                        if i != j) <= 200
model.c4 = pyo.Constraint(model.K, rule = capacity)

model.sub_tour = pyo.ConstraintList()

def get_subtours(sol):
    subtours = []
    LS = len(sol)
    unvisited = [K] + [1 for _ in range(N-1)]
    
    while LS > 0:
        subtour = []
        subtours.append(subtour)
        for i in range(N):
            if unvisited[i]:
                start = i + 1
                break
        
        while True:
            subtour.append(start)
            if unvisited[start - 1]:
                unvisited[start - 1] -= 1
                LS -= 1
            next_node = next((j for (i, j) in sol if i == start and unvisited[j-1]), None)
            
            if next_node == model.N.at(1) or not next_node or not unvisited[next_node - 1]:
                break
            start = next_node
    print(subtours)
    return subtours
            
# Objective Function

def obj_fn(model):
    return pyo.quicksum(x[i, j, k]*times[i, j] 
                        for i in model.N
                        for j in model.N 
                        for k in model.K 
                        if i != j)
model.obj = pyo.Objective(rule = obj_fn, sense = pyo.minimize)

# Solution

sol = SolverFactory("cplex")
res = sol.solve(model)

# Adding subtour Constraints

print(res)

s = x.extract_values()
valid_sol = {(i, j) : round(s[i, j, k]) 
             for i in model.N 
             for j in model.N 
             for k in model.K 
             if i != j and s[i, j, k] and s[i, j, k] >= 0.9}

print(valid_sol)

# while True:
#     sol = SolverFactory("cplex")
#     res = sol.solve(model)
    
#     s = x.extract_values()
#     valid_sol = {(i, j) : round(s[i, j, k])     
#                  for i in model.N 
#                  for j in model.N 
#                  for k in model.K 
#                  if i != j and s[i, j, k] and s[i, j, k] >= 0.9}
#     if not valid_sol:
#         print("No solution exists")
#         break
    
#     subtours = get_subtours(valid_sol)
#     if len(subtours) > K:
#         for subtour in subtours[K:]:
#             for k in model.K:
#                 model.sub_tour.add(
#                     pyo.quicksum(x[i, j, k] 
#                                   for i, j in permutations(subtour, 2)) <= len(subtour) - 1
#                     )
    
#     else:
#         break
    
print(res)

s = x.extract_values()
valid_sol = {(i, j) : round(s[i, j, k]) 
             for i in model.N 
             for j in model.N 
             for k in model.K 
             if i != j and s[i, j, k] and s[i, j, k] >= 0.9}

print(get_subtours(valid_sol))

for tup in permutations([2, 3, 4, 5], 2):
    print(tup)
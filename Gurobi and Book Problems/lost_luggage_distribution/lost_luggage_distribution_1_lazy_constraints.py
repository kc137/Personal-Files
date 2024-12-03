import pyomo.environ as pyo, math, random, time
from pyomo.opt import SolverFactory
from itertools import permutations

# Model

model = pyo.ConcreteModel()

# BigM

M = 100000

N = 17
locations = [*range(1, N+1)]

K = 6
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

model.y = pyo.Var(model.N, model.K, within = pyo.Binary)
y = model.y

model.z = pyo.Var(model.K, within = pyo.Binary)
z = model.z

model.t = pyo.Var(model.K, within = pyo.NonNegativeReals, bounds = (0, 120))
t = model.t

model.s = pyo.Var(within = pyo.NonNegativeReals)
s = model.s

# Constraints

# Van Utilization Constraint

def van_util(model, i, k):
    return y[i, k] <= z[k]
model.c1 = pyo.Constraint(model.N, model.K, rule = van_util)

# Travel Time Constraint

def travel_time_cons(model, k):
    return pyo.quicksum(x[i, j, k]*times[i, j] 
                        for i in model.N 
                        for j in model.C 
                        if i != j) == t[k]
model.c2 = pyo.Constraint(model.K, rule = travel_time_cons)

# Visit Customer Once

def visit_customer(model, j):
    return pyo.quicksum(y[j, k] for k in model.K) == 1
model.c3 = pyo.Constraint(model.C, rule = visit_customer)

# Depot Constraint

def depot_cons(model, k):
    return y[1, k] == z[k]
model.c4 = pyo.Constraint(model.K, rule = depot_cons)

# Arriving at a Location

def arriving_cons(model, j, k):
    return pyo.quicksum(x[i, j, k] for i in model.N 
                        if i != j) == y[j, k]
model.c5 = pyo.Constraint(model.C, model.K, rule = arriving_cons)

# Leaving a Location

def leaving_cons(model, j, k):
    return pyo.quicksum(x[j, i, k] for i in model.N 
                        if i != j) == y[j, k]
model.c6 = pyo.Constraint(model.C, model.K, rule = leaving_cons)

# Symmetry breaking Constraint

def breaking_symmetry(model, k):
    if k < model.K.at(-1):
        return (pyo.quicksum(y[i, k] for i in model.N) 
                >= pyo.quicksum(y[i, k+1] for i in model.N))
    else:
        return pyo.Constraint.Skip
model.c7 = pyo.Constraint(model.K, rule = breaking_symmetry)

model.sub_tour = pyo.ConstraintList()

def get_subtours(sol):
    subtours = []
    LS = len(sol)
    total_origin = sum([1 for (i, j) in sol if i == model.N.at(1)])
    unvisited = [total_origin] + [1 for _ in range(N-1)]
    # print(unvisited)
    
    # print(sol.keys())
    
    while LS > 0:
        subtour = []
        subtours.append(subtour)
        for i in range(N):
            if unvisited[i]:
                start = i+1
                break
        while True:
            subtour.append(start)
            if unvisited[start - 1]:
                unvisited[start - 1] -= 1
                LS -= 1
            next_node = next((j for i, j in sol if i == start and unvisited[j-1]), None)
            
            if next_node == model.N.at(1) or not next_node or not unvisited[next_node - 1]:
                break
            start = next_node
    
    return subtours, total_origin

# Objective Function

def obj_fn(model):
    # return pyo.quicksum(x[i, j, k]*times[i, j]
    #                     for i in model.N 
    #                     for j in model.N 
    #                     for k in model.K 
    #                     if i != j)
    return pyo.quicksum(z[k] for k in model.K)
model.obj = pyo.Objective(rule = obj_fn, sense = pyo.minimize)

# Initial Solution

sol = SolverFactory("cplex")
res = sol.solve(model)

s = x.extract_values()
valid_sol = {(i, j) : round(s[i, j, k]) 
             for i in model.N 
             for j in model.N 
             for k in model.K 
             if i != j and s[i, j, k] and s[i, j, k] >= 0.9}

print(valid_sol)

# Adding the Lazy Constraints

# start = time.time()

while True:
    sol = SolverFactory("cplex")
    res = sol.solve(model)
    
    s = x.extract_values()
    valid_sol = {(i, j) : round(s[i, j, k])     
                 for i in model.N 
                 for j in model.N 
                 for k in model.K 
                 if i != j and s[i, j, k] and s[i, j, k] >= 0.9}
    if not valid_sol:
        print("No solution exists")
        break
    
    subtours, origins = get_subtours(valid_sol)
    if len(subtours) > 5:
        for subtour in subtours[origins:]:
        # for subtour in subtours:
            for k in model.K:
                model.sub_tour.add(
                    pyo.quicksum(x[i, j, k] 
                                  for i, j in permutations(subtour, 2)) <= len(subtour) - 1
                    )
    # if len(subtours) > 5:
    #     subtour = []
    #     for tour in subtours[origins:]:
    #         subtour += tour
    #     print(subtour)
    #     # for subtour in subtours:
    #     for k in model.K:
    #         model.sub_tour.add(
    #             pyo.quicksum(x[i, j, k] 
    #                           for i, j in permutations(subtour, 2)) <= len(subtour) - 1
    #             )
    else:
        break

# Printing the Solution

print(res)

s = x.extract_values()
valid_sol = {(i, j) : round(s[i, j, k]) 
             for i in model.N 
             for j in model.N 
             for k in model.K 
             if i != j and s[i, j, k] and s[i, j, k] >= 0.9}

# print(get_subtours(valid_sol))
print(subtour(valid_sol))
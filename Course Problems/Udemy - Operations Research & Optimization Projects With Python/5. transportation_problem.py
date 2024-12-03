import pyomo.environ as pyo
from pyomo.opt import SolverFactory

# Model

model = pyo.ConcreteModel()

# Parameters
factories = ['A', 'B', 'C']
distribution_centers = [1, 2, 3, 4]
C = {'A': 100, 'B': 150, 'C': 200}
P = {'A': 5, 'B': 4, 'C': 6}
D = {1: 80, 2: 65, 3: 70, 4: 85}
S = {('A', 1): 2, ('A', 2): 3, ('A', 3): 2.5, ('A', 4): 3.5,
     ('B', 1): 2.5, ('B', 2): 2, ('B', 3): 3, ('B', 4): 2.5,
     ('C', 1): 3, ('C', 2): 3.5, ('C', 3): 2, ('C', 4): 2.5}

# Sets

model.factories = pyo.Set(initialize = factories)
factories = model.factories

model.centers = pyo.Set(initialize = distribution_centers)
centers = model.centers

# Variables

model.x = pyo.Var(factories, centers, within = pyo.NonNegativeReals)
x = model.x

model.y = pyo.Var(factories, within = pyo.NonNegativeReals)
y = model.y

# Constraints

def prod_cons(model, s):
    return y[s] <= C[s]
model.c1 = pyo.Constraint(factories, rule = prod_cons)

def supply_cons(model, s):
    return pyo.quicksum(x[s, d] 
                        for d in centers)  == y[s]
model.c2 = pyo.Constraint(factories, rule = supply_cons)

def demand_cons(model, d):
    return pyo.quicksum(x[s, d] 
                        for s in factories) == D[d]
model.c3 = pyo.Constraint(centers, rule = demand_cons)

# Objective Function

def obj_fn(model):
    return (pyo.quicksum(x[i, j]*S[i, j] 
                        for i in factories 
                        for j in centers) + 
            pyo.quicksum(y[i]*P[i] 
                         for i in factories))
model.obj = pyo.Objective(rule = obj_fn, sense = pyo.minimize)

# Solution

sol = SolverFactory("cplex")
res = sol.solve(model)

# Printing the Solution

print(res)

for s in factories:
    print(f"Total products produced in Factory-{s} : {y[s]()}")

for s in factories:
    for d in centers:
        print(f"Quantity supplied from {s} to {d} : {x[s, d]()}")
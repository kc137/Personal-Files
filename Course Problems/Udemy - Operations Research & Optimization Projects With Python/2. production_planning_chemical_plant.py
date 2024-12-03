import pyomo.environ as pyo
from pyomo.opt import SolverFactory

SP = {'A': 20, 'B': 25, 'C': 30}  # Selling price\n
PC = {('A', 1): 12, ('A', 2): 15, ('B', 1): 17, ('B', 2): 16, ('C', 1): 23, ('C', 2): 21}  # Production cost\n
RM = {('A', 1): 3, ('A', 2): 4, ('B', 1): 5, ('B', 2): 3, ('C', 1): 4, ('C', 2): 5}  # Raw material\n
LH = {('A', 1): 2, ('A', 2): 3, ('B', 1): 4, ('B', 2): 2, ('C', 1): 3, ('C', 2): 4}  # Labor hours\n"
Q = {('A', 1): 100, ('A', 2): 80, ('B', 1): 90, ('B', 2): 70, ('C', 1): 60, ('C', 2): 50}  # Capacity\n",
TRM = 500  # Total raw material\n
TLH = 400  # Total labor hours\n

# Model

model = pyo.ConcreteModel()

# Sets and Params

model.chemicals = pyo.Set(initialize = SP.keys())
chemicals = model.chemicals

model.processes = pyo.Set(initialize = [1, 2])
processes = model.processes

# Variables

model.x = pyo.Var(chemicals, processes, within = pyo.NonNegativeReals)
x = model.x

# Constraints

def raw_mat_cons(model):
    return pyo.quicksum(x[i, j]*RM[i, j] 
                        for i in chemicals 
                        for j in processes) <= TRM
model.c1 = pyo.Constraint(rule = raw_mat_cons)

def labor_hr_cons(model):
    return pyo.quicksum(x[i, j]*LH[i, j] 
                        for i in chemicals 
                        for j in processes) <= TLH
model.c2 = pyo.Constraint(rule = labor_hr_cons)

def capacity_cons(model, i, j):
    return x[i, j] <= Q[i, j]
model.c3 = pyo.Constraint(chemicals, processes, rule = capacity_cons)

# Objective Function

def obj_fn(model):
    return pyo.quicksum(
        x[i, j]*(SP[i] - PC[i, j]) 
        for i in chemicals 
        for j in processes
        )
model.obj = pyo.Objective(rule = obj_fn, sense = pyo.maximize)

# Solution

sol = SolverFactory("cplex")
res = sol.solve(model)

# Printing the Solution

print(res)
import pyomo.environ as pyo, gurobipy as gp
from pyomo.opt import SolverFactory

Departments = ['A','B','C','D','E']
Cities = ['Bristol', 'Brighton', 'London']

# Create a dictionary to capture benefits -in thousands of dollars from relocation.

d2c, benefit = gp.multidict({
    ('A', 'Bristol'): 10,
    ('A', 'Brighton'): 10,
    ('A', 'London'): 0,
    ('B', 'Bristol'): 15,
    ('B', 'Brighton'): 20,
    ('B', 'London'): 0,
    ('C', 'Bristol'): 10,
    ('C', 'Brighton'): 15,
    ('C', 'London'): 0,
    ('D', 'Bristol'): 20,
    ('D', 'Brighton'): 15,
    ('D', 'London'): 0,
    ('E', 'Bristol'): 5,
    ('E', 'Brighton'): 15,
    ('E', 'London'): 0
})

dcd2c2, communicationCost = gp.multidict({
    ('A','London','C','Bristol'): 13,
    ('A','London','C','Brighton'): 9,
    ('A','London','C','London'): 10,
    ('A','London','D','Bristol'): 19.5,
    ('A','London','D','Brighton'): 13.5,
    ('A','London','D','London'): 15,
    ('B','London','C','Bristol'): 18.2,
    ('B','London','C','Brighton'): 12.6,
    ('B','London','C','London'): 14,
    ('B','London','D','Bristol'): 15.6,
    ('B','London','D','Brighton'): 10.8,
    ('B','London','D','London'): 12,
    ('C','London','E','Bristol'): 26,
    ('C','London','E','Brighton'): 18,
    ('C','London','E','London'): 20,
    ('D','London','E','Bristol'): 9.1,
    ('D','London','E','Brighton'): 6.3,
    ('D','London','E','London'): 7,
    ('A','Bristol','C','Bristol'): 5,
    ('A','Bristol','C','Brighton'): 14,
    ('A','Bristol','C','London'): 13,
    ('A','Bristol','D','Bristol'): 7.5,
    ('A','Bristol','D','Brighton'): 21,
    ('A','Bristol','D','London'): 19.5,
    ('B','Bristol','C','Bristol'): 7,
    ('B','Bristol','C','Brighton'): 19.6,
    ('B','Bristol','C','London'): 18.2,
    ('B','Bristol','D','Bristol'): 6,
    ('B','Bristol','D','Brighton'): 16.8,
    ('B','Bristol','D','London'): 15.6,
    ('C','Bristol','E','Bristol'): 10,
    ('C','Bristol','E','Brighton'): 28,
    ('C','Bristol','E','London'): 26,
    ('D','Bristol','E','Bristol'): 3.5,
    ('D','Bristol','E','Brighton'): 9.8, 
    ('D','Bristol','E','London'): 9.1,
    ('A','Brighton','C','Bristol'): 14,
    ('A','Brighton','C','Brighton'): 5,
    ('A','Brighton','C','London'): 9,
    ('A','Brighton','D','Bristol'): 21,
    ('A','Brighton','D','Brighton'): 7.5,
    ('A','Brighton','D','London'): 13.5,
    ('B','Brighton','C','Bristol'): 19.6,
    ('B','Brighton','C','Brighton'): 7,
    ('B','Brighton','C','London'): 12.6,
    ('B','Brighton','D','Bristol'): 16.8,
    ('B','Brighton','D','Brighton'): 6,
    ('B','Brighton','D','London'): 10.8,
    ('C','Brighton','E','Bristol'): 28,
    ('C','Brighton','E','Brighton'): 10,
    ('C','Brighton','E','London'): 18,
    ('D','Brighton','E','Bristol'): 9.8,
    ('D','Brighton','E','Brighton'): 3.5,
    ('D','Brighton','E','London'): 6.3
})

# Model

model = pyo.ConcreteModel()

# Variables

model.locate = pyo.Var(d2c, within = pyo.Binary)
locate = model.locate

model.y = pyo.Var(dcd2c2, within = pyo.Binary)
y = model.y

# Constraints

def dept_once(model, d):
    return pyo.quicksum(locate[d, c] for c in Cities) == 1
model.c1 = pyo.Constraint(Departments, rule = dept_once)

def city_thrice(model, c):
    return pyo.quicksum(locate[d, c] for d in Departments) <= 3
model.c2 = pyo.Constraint(Cities, rule = city_thrice)

model.logical = pyo.ConstraintList()

for d, c, d2, c2 in dcd2c2:
    model.logical.add(
        y[d, c, d2, c2] <= locate[d, c]
        )
    model.logical.add(
        y[d, c, d2, c2] <= locate[d2, c2]
        )
    model.logical.add(
        locate[d, c] + locate[d2, c2] - y[d, c, d2, c2] <= 1
        )

# Objective Function

def obj_fn(model):
    return (pyo.quicksum(benefit[d, c]*locate[d, c] 
                        for d in Departments 
                        for c in Cities) # for d, c in d2c
            - pyo.quicksum(communicationCost[d, c, d2, c2]*y[d, c, d2, c2] 
                           for d, c, d2, c2 in dcd2c2))
model.obj = pyo.Objective(rule = obj_fn, sense = pyo.maximize)

# Solution

sol = SolverFactory("cplex")
res = sol.solve(model)

for d, c in d2c:
    if locate[d, c]() and locate[d, c]() >= 0.9:
        print(f"locate[{d}, {c}] = {locate[d, c]()}")

benefits = pyo.quicksum(benefit[d, c]*locate[d, c]() 
                        for d, c in d2c)
communications_cost = pyo.quicksum(communicationCost[d, c, d2, c2]*y[d, c, d2, c2]() 
                                   for d, c, d2, c2 in dcd2c2)

for d, c, d2, c2 in dcd2c2:
    if y[d, c, d2, c2]() and y[d, c, d2, c2]() >= 0.9:
        print(f"y[{d, c, d2, c2}] = {y[d, c, d2, c2]()}")

print(f"Total yearly benefit : ${benefits*1000}")
print(f"Total yearly communication cost : ${round(communications_cost*1000)}")
print(f"Total yearly profit : ${round((benefits - communications_cost)*1000)}")

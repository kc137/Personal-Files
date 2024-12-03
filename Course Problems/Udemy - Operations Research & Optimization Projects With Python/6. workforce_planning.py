import pyomo.environ as pyo
from pyomo.opt import SolverFactory

# Model

model = pyo.ConcreteModel()

# Parameters (example values)
D = [100, 120, 110, 130, 140, 135, 130, 125, 120, 115, 110, 105]  # Monthly demand
C_H = 500  # Cost of hiring
C_F = 300  # Cost of firing
C_S = 2000  # Monthly salary
MaxH = 20  # Max hiring per month
MaxF = 15  # Max firing per month
E_0 = 100  # Initial employees

# Sets

model.months = pyo.RangeSet(1, 12)
months = model.months

# Variables

# Employees
model.E = pyo.Var(months, within = pyo.NonNegativeIntegers)
E = model.E

# Hiring Employees
model.H = pyo.Var(months, within = pyo.NonNegativeIntegers)
H = model.H

# Firing Employees
model.F = pyo.Var(months, within = pyo.NonNegativeIntegers)
F = model.F

# Constraints

def employee_balance(model, m):
    if m == 1:
        return E[m] == E_0 + H[m] - F[m]
    return E[m] == E[m-1] + H[m] - F[m]
model.c1 = pyo.Constraint(months, rule = employee_balance)

def hiring_cons(model, m):
    return (0, H[m], MaxH)
model.c2 = pyo.Constraint(months, rule = hiring_cons)

def firing_cons(model, m):
    return (0, F[m], MaxF)
model.c3 = pyo.Constraint(months, rule = firing_cons)

def employee_demand_cons(model, m):
    return E[m] >= D[m-1]
model.c4 = pyo.Constraint(months, rule = employee_demand_cons)

# Objective Function

def obj_fn(model):
    return pyo.quicksum((E[m]*C_S) + (H[m]*C_H) + (F[m]*C_F) 
                        for m in months)
model.obj = pyo.Objective(rule = obj_fn, sense = pyo.minimize)

# Solution

sol = SolverFactory("cplex")
res = sol.solve(model)

# Printing the Solution

print(res)
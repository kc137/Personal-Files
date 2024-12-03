import pyomo.environ as pyo
from fleet_planning_data import demands, initial_stock, cm, costs
from pyomo.opt import SolverFactory

# Model

model = pyo.ConcreteModel()

# Sets and Params

model.contr = pyo.RangeSet(3, 5)
contr = model.contr

model.months = pyo.RangeSet(1, 6)
months = model.months

# Variables

model.rent = pyo.Var(contr, months, within = pyo.NonNegativeIntegers)
rent = model.rent

# Constraints

def requirement_cons(model, m):
    return ((initial_stock 
            if m <= 2 
            else 0) + 
            pyo.quicksum(rent[per, mon] for per, mon in cm[m-1]) 
            >= demands[m-1])
model.c1 = pyo.Constraint(months, rule = requirement_cons)

# Objective Function

def obj_fn(model):
    return pyo.quicksum(costs[c]*rent[c, m] 
                        for c in contr 
                        for m in months)
model.obj = pyo.Objective(rule = obj_fn, sense = pyo.minimize)

# Solution

sol = SolverFactory("cplex")
res = sol.solve(model)

# Printing the Solution

print(res)

for m in months:
    total_available = ((initial_stock if m <= 2 else 0) + 
                    pyo.quicksum(rent[c, m]() 
                                 for c in contr))
    print(f"Cars available in month-{m} : {total_available}")
    
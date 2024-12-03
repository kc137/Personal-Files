import pyomo.environ as pyo
from pyomo.opt import SolverFactory

# Model

model = pyo.ConcreteModel()

# Data

share_prices = [100, 50, 80, 40]

returns = [0.12, 0.08, 0.06, 0.1]

risks = [0.1, 0.07, 0.05, 0.08]

total_investment = 200000

# Sets

model.types = pyo.RangeSet(1, 4)
types = model.types

# Variables

model.x = pyo.Var(types, within = pyo.NonNegativeReals)
# model.x = pyo.Var(types, within = pyo.NonNegativeIntegers)
x = model.x

# Constraints

def max_investment_cons(model, t):
    return share_prices[t-1]*x[t] <= 0.5*total_investment
model.c1 = pyo.Constraint(types, rule = max_investment_cons)

def min_return_cons(model):
    return pyo.quicksum(share_prices[t-1]*x[t]*(returns[t-1]) 
                       for t in types) >= 0.09*total_investment
model.c2 = pyo.Constraint(rule = min_return_cons)

def total_investment_cons(model):
    return pyo.quicksum(x[t]*share_prices[t-1] for t in types) == total_investment
model.c3 = pyo.Constraint(rule = total_investment_cons)

# Objective Function

def obj_fn(model):
    return pyo.quicksum(share_prices[t-1]*x[t]*risks[t-1] 
                        for t in types)
# model.obj = pyo.Objective(rule = obj_fn, sense = pyo.minimize)

def obj_fn_2(model):
    return pyo.quicksum(share_prices[t-1]*x[t]*returns[t-1] 
                        for t in types)
model.obj = pyo.Objective(rule = obj_fn_2, sense = pyo.maximize)

# Solution

sol = SolverFactory("cplex", solver_io = "python")
res = sol.solve(model)

# Printing the Solution

print(res)

for t in types:
    print(f"Total shares purchased : {x[t]()}")
    print(f"The amount invested in type-{t} : {x[t]()*share_prices[t-1]}$")

total_risk = pyo.quicksum(share_prices[t-1]*x[t]()*risks[t-1] 
                          for t in types)
print(f"Total amount of risk : {total_risk}$")
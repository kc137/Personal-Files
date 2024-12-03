import pyomo.environ as pyo
from pyomo.opt import SolverFactory

# Model

model = pyo.ConcreteModel()

# Data

salaries = [300, 400, 150, 50]

prod_per_week = [10, 5, 5, 1]

demands = [52, 65, 70, 85]

curr_artisans = 6

# Sets

model.types = pyo.RangeSet(1, 4)
types = model.types

model.weeks = pyo.RangeSet(1, 4)
weeks = model.weeks

# Variables

model.x = pyo.Var(types, weeks, within = pyo.NonNegativeIntegers)
x = model.x

model.z = pyo.Var(weeks, within = pyo.NonNegativeIntegers)
z = model.z

# Cosntraints

def balance_cons(model, w):
    if w <= 2:
        return x[1, w] + x[2, w] == (curr_artisans if w == 1 else x[1, w-1] + x[2, w-1])
    else:
        return x[1, w] + (x[2, w] if w <= 3 else 0) == x[1, w-1] + x[2, w-1] + x[3, w-1]
model.c1 = pyo.Constraint(weeks, rule = balance_cons)

model.week_2_4 = pyo.ConstraintList()

for w in weeks:
    if w >= 2:
        model.week_2_4.add(
            x[3, w] == x[4, w-1]
            )
    if w == 4:
        model.week_2_4.add(x[1, w] >= 9)

model.demand_cons = pyo.ConstraintList()

for w in weeks:
    if w <= 1:
        expr_1 = pyo.quicksum(x[t, w]*prod_per_week[t-1] 
                            for t in types if t != 3)
        model.demand_cons.add(expr_1 >= demands[w-1])
    elif w <= 3:
        expr_2 = pyo.quicksum(x[t, w]*prod_per_week[t-1] 
                            for t in types) + z[w-1]
        model.demand_cons.add(expr_2 >= demands[w-1])
        model.demand_cons.add(z[w] == expr_2 - demands[w-1])
    else:
        model.demand_cons.add(pyo.quicksum(x[t, w]*prod_per_week[t-1] 
                            for t in types if t not in [2, 4]) + z[w-1] >= demands[w-1])

# Objective Function

def obj_fn(model):
    return pyo.quicksum(x[t, w]*salaries[t-1] 
                        for t in types 
                        for w in weeks)
model.obj = pyo.Objective(rule = obj_fn, sense = pyo.minimize)

# Solution

sol = SolverFactory("cplex", solver_io = "python")
res = sol.solve(model)

# Printing the Solution

print(res)

for t in types:
    for w in weeks:
        print(f"Total type-{t} of workers work in week-{w} : {x[t, w]()}")

for w in weeks:
    print(f"Overproduction in week-{w} : {z[w]()}")


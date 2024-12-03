import pyomo.environ as pyo, pandas as pd
from pyomo.opt import SolverFactory

# Model

model = pyo.ConcreteModel()

# Sets and Params

model.e = pyo.RangeSet(1, 5)
model.s = pyo.RangeSet(1, 21)

# Variables

model.x = pyo.Var(model.e, model.s, within = pyo.Binary)
x = model.x

model.y = pyo.Var(model.e, within = pyo.Binary)
y = model.y

# Constraints

# 16 Rest Hours before and after assignment

def rest_cons(model, e, s):
    return pyo.quicksum(x[e, k%3 if k > model.s.at(-1) else k] for k in range(s, s+3)) <= 1
model.c1 = pyo.Constraint(model.e, model.s, rule = rest_cons)

# Personnel per shift

def per_shift(model, s):
    return pyo.quicksum(x[e, s] for e in model.e) >= 1
model.c2 = pyo.Constraint(model.s, rule = per_shift)

# def night_shift_limit(model, e, s):
#     if s%3 == 1:
#         return x[e, s] + x[e, s+1] >= 2*x[e, s+2]
#     else:
#         return pyo.Constraint.Skip
# model.c3 = pyo.Constraint(model.e, model.s, rule = night_shift_limit)

model.night_shift_limit = pyo.ConstraintList()

for e in model.e:
    model.night_shift_limit.add(
        pyo.quicksum(x[e, 3*d] for d in range(1, 8)) 
        <= pyo.quicksum(x[e, 1 + d*3] for d in range(6))
        )
    model.night_shift_limit.add(
        pyo.quicksum(x[e, 3*d] for d in range(1, 8)) 
        <= pyo.quicksum(x[e, 2 + d*3] for d in range(6))
        )

# Weekly total shifts

def weekly_shifts(model, e):
    return pyo.quicksum(x[e, s] for s in model.s) == 6*y[e]
model.c4 = pyo.Constraint(model.e, rule = weekly_shifts)

# Objective Function

def obj_fn(model):
    return pyo.quicksum(y[e] for e in model.e)
model.obj = pyo.Objective(rule = obj_fn, sense = pyo.maximize)

# Solution

sol = SolverFactory("cplex")
res = sol.solve(model)

# Printing the Solution

res_dict = {d : [[0]*model.e.at(-1) for _ in range(3)] for d in range(1, 8)}

for e in model.e:
    for s in model.s:
        if x[e, s]() and x[e, s]() >= 0.9:
            d = (s//3) + 1 if s%3 else (s//3)
            shift = s%3 if s%3 else 3
            # res_dict[d][shift-1][e-1] = int(x[e, s]())
            res_dict[d][shift-1][e-1] = e

res_df = pd.DataFrame.from_dict(res_dict, orient = "index", 
                                columns = ["Morning", "Afternoon", "Night"])
res_df.index = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
print(res_df)
res_df.to_excel("res.xlsx")

for e in model.e:
    print(f"Employee-{e} assigned : {sum(x[e, s]() for s in model.s)}-shifts")
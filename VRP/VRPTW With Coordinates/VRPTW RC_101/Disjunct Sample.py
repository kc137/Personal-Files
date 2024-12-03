import pyomo.environ as pyo, pyomo.gdp as dp
from pyomo.opt import SolverFactory

model = pyo.ConcreteModel()

# Sets and Parameters

model.N = pyo.RangeSet(1, 5)
model.C = pyo.RangeSet(2, 5)
model.V = pyo.RangeSet(1, 2)

ub_val = [10, 20, 30, 60, 70]
model.ub = pyo.Param(model.N, domain = pyo.Any, initialize = {model.N.at(i) : 
                                                              ub_val[i-1] for i in model.N})
ub = model.ub

# Variables

model.s = pyo.Var(model.N, model.V, domain = pyo.NonNegativeReals, bounds = (0, 100))
s = model.s
model.m = pyo.Var(model.N, domain = pyo.NonNegativeReals, bounds = (0, 100))
m = model.m

# Constraints

def s_val(model, i, k):
    if i != 1:
        return s[i, k] == 50
    else:
        return s[i, k] == 0
model.s_vals = pyo.Constraint(model.N, model.V, rule = s_val)

def dis1(model, j, k):    
    d1 = dp.Disjunct()
    d1.s_less = pyo.Constraint(expr = s[j, k] <= ub[j])
    d1.mj_zero = pyo.Constraint(expr = m[j] == 0)
    model.add_component(f"d1_{j}_{k}", d1)
    return d1

def dis2(model, j, k):
    d2 = dp.Disjunct()
    d2.s_greater = pyo.Constraint(expr = s[j, k] >= ub[j])
    d2.mj_nonzero = pyo.Constraint(expr =  m[j] == s[j, k] - ub[j])
    model.add_component(f"d2_{j}_{k}", d2)
    return d2

def disj_test(model, j, k):
    fst = dis1(model, j, k)
    snd = dis2(model, j, k)
    return [fst, snd]

model.disj = dp.Disjunction(model.N, model.V, rule = disj_test)

# --transform pyomo.gdp.bigm


pyo.TransformationFactory('gdp.hull').apply_to(model)


# model.mcons = pyo.ConstraintList()
# for k in model.V:
#     for i in model.N:
#         model.mcons.add(m[i] == ub[i] - s[i, k])

# Objective

model.Obj = pyo.Objective(expr = sum(m[i] for i in model.N), sense = pyo.minimize)

# Solution

sol = SolverFactory("cplex")
res = sol.solve(model)

for i in model.N:
    print(f"{m[i]} = {round(m[i]())}")
for k in model.V:
    for i in model.N:
        print(f"{s[i, k]} = {s[i, k]()}")
        
print(f"Min. Service Time Difference {m} = {model.Obj()}")
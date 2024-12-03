import pyomo.environ as pyo, pyomo.gdp as dp
from pyomo.opt import SolverFactory

model = pyo.ConcreteModel()

# Sets and Parameters

model.N = pyo.RangeSet(1, 5)
model.C = pyo.RangeSet(2, 5)
model.V = pyo.RangeSet(1, 2)

lb_val = [0, 10, 30, 50, 70]
ub_val = [10, 20, 40, 70, 100]

model.ub = pyo.Param(model.N, domain = pyo.Any, initialize = {model.N.at(i) : 
                                                              ub_val[i-1] for i in model.N})
ub = model.ub

model.lb = pyo.Param(model.N, domain = pyo.Any, initialize = {model.N.at(i) : 
                                                              lb_val[i-1] for i in model.N})
lb = model.lb

# Variables

model.s = pyo.Var(model.N, model.V, domain = pyo.NonNegativeReals, bounds = (0, 100))
s = model.s
model.m = pyo.Var(model.N, domain = pyo.NonNegativeReals, bounds = (0, 1000))
m = model.m
model.sm = pyo.Var(model.N, domain = pyo.NonNegativeReals, bounds = (0, 1000))
sm = model.sm

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

def disj_test1(model, j, k):
    fst = dis1(model, j, k)
    snd = dis2(model, j, k)
    return [fst, snd]

model.disj1 = dp.Disjunction(model.N, model.V, rule = disj_test1)

def dis3(model, j, k):    
    d3 = dp.Disjunct()
    d3.s_less = pyo.Constraint(expr = s[j, k] >= lb[j])
    d3.mj_zero = pyo.Constraint(expr = sm[j] == 0)
    model.add_component(f"d3_{j}_{k}", d3)
    return d3

def dis4(model, j, k):
    d4 = dp.Disjunct()
    d4.s_greater = pyo.Constraint(expr = s[j, k] <= lb[j])
    d4.mj_nonzero = pyo.Constraint(expr =  sm[j] == lb[j] - s[j, k])
    model.add_component(f"d4_{j}_{k}", d4)
    return d4

def disj_test2(model, j, k):
    fst = dis3(model, j, k)
    snd = dis4(model, j, k)
    return [fst, snd]

model.disj2 = dp.Disjunction(model.N, model.V, rule = disj_test2)

# --transform pyomo.gdp.bigm


pyo.TransformationFactory('gdp.hull').apply_to(model)


# model.mcons = pyo.ConstraintList()
# for k in model.V:
#     for i in model.N:
#         model.mcons.add(m[i] == ub[i] - s[i, k])

# Objective

lb_sum = sum(sm[i] for i in model.N)
ub_sum = sum(m[i] for i in model.N)

def Obj_Fn(model):
    return lb_sum + ub_sum

model.Obj = pyo.Objective(rule = Obj_Fn, sense = pyo.minimize)

# Solution

sol = SolverFactory("cplex")
res = sol.solve(model)

for i in model.N:
    print(f"{m[i]} = {round(m[i]())}")
for i in model.N:
    print(f"{sm[i]} = {round(sm[i]())}")
for k in model.V:
    for i in model.N:
        print(f"{s[i, k]} = {s[i, k]()}")
        
print(f"Min. Service Time Difference {m} = {model.Obj()}")
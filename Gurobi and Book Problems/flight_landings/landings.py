import pyomo.environ as pyo
from pyomo.opt import SolverFactory
from landings_data import START, TARGET, STOP, EARLY, LATE, DIST

# Model

model = pyo.ConcreteModel()

# Sets and Params

model.planes = pyo.RangeSet(1, 10)
planes = model.planes

M = [[0]*10 for _ in range(10)]

for p in range(10):
    for q in range(10):
        M[p-1][q-1] = STOP[p-1] + DIST[p-1][q-1] - START[q-1]

# Variables

model.land = pyo.Var(planes, within = pyo.NonNegativeReals)
land = model.land

model.prec = pyo.Var(planes, planes, within = pyo.Binary)
prec = model.prec

model.early = pyo.Var(planes, within = pyo.NonNegativeReals)
early = model.early

model.late = pyo.Var(planes, within = pyo.NonNegativeReals)
late = model.late

# Constraints

def bounds(model, p):
    return (START[p-1], land[p], STOP[p-1])
model.c1 = pyo.Constraint(planes, rule = bounds)

def only_one_prec(model, p, q):
    if p != q:
        return prec[p, q] + prec[q, p] == 1
    else:
        return pyo.Constraint.Skip
model.c2 = pyo.Constraint(planes, planes, rule = only_one_prec)

def time_precedence(model, p, q):
    if p != q:
        return land[p] + DIST[p-1][q-1] <= land[q] + M[p-1][q-1]*prec[q, p]
    else:
        return pyo.Constraint.Skip
model.c3 = pyo.Constraint(planes, planes, rule = time_precedence)

def early_bounds(model, p):
    return (0, early[p], TARGET[p-1] - START[p-1])
model.c4 = pyo.Constraint(planes, rule = early_bounds)

def late_bounds(model, p):
    return (0, late[p], STOP[p-1] - TARGET[p-1])
model.c5 = pyo.Constraint(planes, rule = late_bounds)

def land_cons(model, p):
    return land[p] == TARGET[p-1] - early[p] + late[p]
model.c6 = pyo.Constraint(planes, rule = land_cons)

# Objective Function

def obj_fn(model):
    return (pyo.quicksum(EARLY[p-1]*early[p] 
                        for p in planes) 
            + pyo.quicksum(LATE[p-1]*late[p] 
                                for p in planes))
model.obj = pyo.Objective(rule = obj_fn, sense = pyo.minimize)

# Solution

sol = SolverFactory("cplex")
res = sol.solve(model)

# Printing the Solution

print(res)

for p in planes:
    print(f"Plane arrives at time-{round(land[p]())}")
    
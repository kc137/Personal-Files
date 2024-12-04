import pyomo.environ as pyo, logging
from pyomo.opt import SolverFactory
from pyomo.util.infeasible import log_infeasible_constraints
from data import NC, ND, NV, coords, demands, time_windows, service_time, \
    max_dur, Q, distance_matrix

M = 1000

# Model

model = pyo.ConcreteModel()

# Sets and Params

model.N = pyo.RangeSet(1, NC + ND)
model.C = pyo.RangeSet(1, NC)
model.D = pyo.RangeSet(NC+1, NC+ND)
model.V = pyo.RangeSet(1, NV)

# Variables

x_var_list = [(i, j, k) 
              for i in model.N 
              for j in model.N 
              for k in model.V 
              if i != j]

model.x = pyo.Var(x_var_list, within = pyo.Binary)
x = model.x

model.z = pyo.Var(model.D, within = pyo.Binary)
z = model.z

model.s = pyo.Var(model.N, within = pyo.NonNegativeReals)
s = model.s

# Constraints

def flow(model, j, k):
    return (pyo.quicksum(x[i, j, k] for i in model.N if i != j) 
            == pyo.quicksum(x[j, i, k] for i in model.N if i != j))
model.c1 = pyo.Constraint(model.N, model.V, rule = flow)

def once(model, j):
    return pyo.quicksum(x[i, j, k] 
                        for i in model.N 
                        for k in model.V 
                        if i != j) == 1
model.c2 = pyo.Constraint(model.C, rule = once)

def vehi_at_most_once(model, k):
    return pyo.quicksum(x[i, j, k] 
                        for i in model.D 
                        for j in model.C) <= 1
model.c3 = pyo.Constraint(model.V, rule = vehi_at_most_once)

def less_than_depots(model, j, k):
    return pyo.quicksum(x[i, j, k] 
                        for i in model.N
                        if i != j) <= z[j]
model.c4 = pyo.Constraint(model.D, model.V, rule = less_than_depots)

def demand_cons(model, k):
    return pyo.quicksum(x[i, j, k]*demands[i-1] 
                        for i in model.N 
                        for j in model.C 
                        if i != j) <= Q
model.c5 = pyo.Constraint(model.V, rule = demand_cons)

model.time_cons = pyo.ConstraintList()

for i in model.N:
    for j in model.C:
        if i != j:
            model.time_cons.add(
                (s[i] + service_time[i-1] + distance_matrix[i-1][j-1] 
                 <= s[j] + M*(1 - pyo.quicksum(x[i, j, k] 
                                               for k in model.V)) + 0.001)
                )

# Objective Function

"""
pyo.quicksum(M*z[d] 
             for d in model.D) 
"""

def obj_fn(model):
    return (pyo.quicksum(x[i, j, k]*distance_matrix[i-1][j-1] 
                         for i in model.N 
                         for j in model.N 
                         for k in model.V 
                         if i != j))
model.obj = pyo.Objective(rule = obj_fn, sense = pyo.minimize)

# Solution

sol = SolverFactory("cplex")
sol.options["timelimit"] = 15
res = sol.solve(model)

# Printing the Solution

print(res)

vehi_dict = {v : [] for v in model.V}

for k in model.V:
    for i in model.N:
        for j in model.N:
            if i != j and x[i, j, k]() and x[i, j, k]() >= 0.9:
                vehi_dict[k].append((i, j))

"""
{1: [(2, 52),
  (9, 42),
  (31, 44),
  (32, 9),
  (36, 31),
  (41, 36),
  (42, 46),
  (43, 2),
  (44, 32),
  (46, 43),
  (49, 41)],
 2: [(4, 19),
  (7, 10),
  (10, 34),
  (14, 4),
  (19, 28),
  (22, 50),
  (28, 7),
  (34, 45),
  (45, 22),
  (51, 14)],
 3: [(12, 38),
  (15, 30),
  (17, 18),
  (18, 26),
  (21, 12),
  (23, 25),
  (24, 21),
  (25, 15),
  (26, 23),
  (30, 47),
  (38, 40),
  (39, 52),
  (40, 17),
  (47, 39),
  (52, 24)],
 4: [(1, 29),
  (3, 6),
  (5, 16),
  (6, 27),
  (8, 5),
  (11, 48),
  (13, 8),
  (16, 35),
  (20, 33),
  (27, 50),
  (29, 20),
  (33, 13),
  (35, 37),
  (37, 11),
  (48, 3),
  (51, 1)]}
"""






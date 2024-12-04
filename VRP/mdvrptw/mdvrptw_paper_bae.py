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
                        for i in model.C 
                        for j in model.N 
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
{1: [(3, 27),
  (6, 37),
  (9, 42),
  (10, 11),
  (11, 45),
  (27, 48),
  (37, 9),
  (39, 50),
  (42, 46),
  (43, 39),
  (45, 6),
  (46, 43),
  (48, 10),
  (50, 3)],
 2: [(7, 41),
  (22, 7),
  (31, 44),
  (32, 35),
  (34, 50),
  (35, 34),
  (36, 31),
  (41, 36),
  (44, 32),
  (50, 22)],
 3: [(1, 14),
  (4, 19),
  (5, 8),
  (8, 13),
  (13, 33),
  (14, 51),
  (16, 29),
  (19, 1),
  (20, 28),
  (28, 4),
  (29, 5),
  (33, 20),
  (51, 16)],
 4: [(2, 52),
  (12, 21),
  (15, 25),
  (17, 40),
  (18, 17),
  (21, 24),
  (23, 26),
  (24, 2),
  (25, 23),
  (26, 18),
  (30, 15),
  (38, 12),
  (40, 38),
  (47, 30),
  (52, 47)]}
"""







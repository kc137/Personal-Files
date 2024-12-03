import pyomo.environ as pyo, pyomo.gdp as dp
from pyomo.opt import SolverFactory
from jsp_10j_10m_f10_data import processing_times as pt, machine_sequence as ms

# from itertools import permutations

# lst = [n for n in range(1, 11)]

# p_lst = permutations(lst, 2)

# for perm in p_lst:
#     print(perm)

model = pyo.ConcreteModel()

NJ = len(pt)
NM = len(pt[0])
M = 2000

# Sets and Parameters

model.j = pyo.RangeSet(1, 10)
model.m = pyo.RangeSet(1, 10)
model.m2 = pyo.RangeSet(2, 10)
model.t = pyo.RangeSet(1, 450)
model.a1 = [0]
model.a2 = [0]

model.times = pyo.Param(model.j, model.m, within = pyo.Any, 
                        initialize = {
                            (j, m) : pt[j-1][m-1] 
                            for j in model.j 
                            for m in model.m
                            })
processing_times = model.times

model.m_seq = pyo.Param(model.j, model.m, within = pyo.Any, 
                        initialize = {
                            (j, m) : ms[j-1][m-1] 
                            for j in model.j 
                            for m in model.m
                            })
machine_sequence = model.m_seq

model.disj_seq = pyo.Param(model.j, model.m, within = pyo.Any, 
                        initialize = {
                            (j, m) : m
                            for j in model.j 
                            for m in model.m
                            })
disj_seq = model.disj_seq

# Variables

model.x = pyo.Var(model.t, within = pyo.Binary)
x = model.x

model.start = pyo.Var(model.j, model.m, within = pyo.NonNegativeReals, bounds = (0, M))
start = model.start

model.makespan = pyo.Var(within = pyo.NonNegativeReals)
makespan = model.makespan

# Constraints

# def start_time(model, j, m):
#     return start[j, machine_sequence[j, m-1]] + processing_times[j, machine_sequence[j, m-1]] <= start[j, machine_sequence[j, m]]
# model.c1 = pyo.Constraint(model.j, model.m2, rule = start_time)

model.conjunctions = pyo.ConstraintList()

for m in model.m:
    for j in range(2, model.j.at(-1) + 1):
        model.conjunctions.add(start[machine_sequence[m, j-1], m] + processing_times[machine_sequence[m, j-1], m] <= start[machine_sequence[m, j], m])

def finish_time(model, j):
    return start[machine_sequence[j, model.m.at(-1)], j] + processing_times[machine_sequence[j, model.m.at(-1)], j] <= makespan
model.c2 = pyo.Constraint(model.j, rule = finish_time)

for m in model.m:
    for j in model.j:
        for k in range(model.j.at(j) + 1, model.j.at(-1) + 1):
            model.a1.append(start[m, disj_seq[m, j]] 
                        + processing_times[m, disj_seq[m, j]] 
                        <= start[m, disj_seq[m, k]])
            model.a2.append(start[m, disj_seq[m, k]] 
                        + processing_times[m, disj_seq[m, k]] 
                        <= start[m, disj_seq[m, j]])

# y_len = 1
# for m in model.m:
#     for j in model.j:
#         for k in range(model.j.at(j) + 1, model.j.at(-1) + 1):
#             model.a1.add(start[m, disj_seq[m, j]] 
#                         + processing_times[m, disj_seq[m, j]] 
#                         <= start[m, disj_seq[m, k]] + M*x[y_len])
#             model.a1.add(start[m, disj_seq[m, k]] 
#                         + processing_times[m, disj_seq[m, k]] 
#                         <= start[m, disj_seq[m, j]] + M*(1 - x[y_len]))
#             y_len += 1

def disj1(model, a):
    d1 = dp.Disjunct()
    d1.cons = pyo.Constraint(expr = model.a1[a])
    model.add_component(f"d1_{a}", d1)
    return d1

def disj2(model, b):
    d2 = dp.Disjunct()
    d2.cons = pyo.Constraint(expr = model.a2[b])
    model.add_component(f"d2_{b}", d2)
    return d2

def final_disj(model, a):
    fst = disj1(model, a)
    snd = disj2(model, a)
    return [fst, snd]

model.disj = dp.Disjunction(model.t, rule = final_disj)

pyo.TransformationFactory("gdp.bigm").apply_to(model)


def obj_fn(model):
    return makespan
model.obj = pyo.Objective(rule = obj_fn, sense = pyo.minimize)

# Solution

sol = SolverFactory("cplex")
sol.options["timelimit"] = 5
res = sol.solve(model)

# Printing the Solution

print(res)
print(f"The Makespan for 10-J 10-M Fischer Instance : {model.obj()} min.")

"""
Problem: 
- Name: tmprfrzlao4
  Lower bound: 827.0
  Upper bound: 953.9999999929998
  Number of objectives: 1
  Number of constraints: 1450
  Number of variables: 1001
  Number of nonzeros: 3800
  Sense: minimize
Solver: 
- Status: ok
  User time: 30.11
  Termination condition: maxTimeLimit
  Termination message: MIP - Time limit exceeded, integer feasible\x3a Objective = 9.5399999999e+02
  Error rc: 0
  Time: 30.4061336517334
Solution: 
- number of solutions: 0
  number of solutions displayed: 0

The Makespan for 10-J 10-M Fischer Instance : 953.9999999929998 min.
"""


"""
Problem: 
- Name: tmp78pejusf
  Lower bound: 749.0
  Upper bound: 1144.999999994
  Number of objectives: 1
  Number of constraints: 4150
  Number of variables: 2801
  Number of nonzeros: 10100
  Sense: minimize
Solver: 
- Status: ok
  User time: 15.13
  Termination condition: maxTimeLimit
  Termination message: MIP - Time limit exceeded, integer feasible\x3a Objective = 1.1450000000e+03
  Error rc: 0
  Time: 17.563529014587402
Solution: 
- number of solutions: 0
  number of solutions displayed: 0

The Makespan for 10-J 10-M Fischer Instance : 1144.999999994 min.
"""





import pyomo.environ as pyo
# import matplotlib.pyplot as plt
# import pandas as pd
import json
from pyomo.opt import SolverFactory

path = "F:\\Solvers\\CPLEX_2211\\cplex\\bin\\x64_win64\\cplex.exe"

sequences = []
pt = []

with open("la18.txt", "r") as data:
    lines = data.read().splitlines()
    
    for line in lines[1:]:
        mc, pr = [], []
        curr = line.split()
        for i in range(len(curr)):
            if i % 2 == 0:
                mc.append(int(curr[i]))
            else:
                pr.append(int(curr[i]))
        sequences.append(mc)
        pt.append(pr)

precedences = [(row[i], row[i+1], j)
               for j, row in enumerate(sequences)
               for i in range(len(sequences[0]) - 1)]


# with open("data/random_10_10.json") as data:
#     data = json.load(data)
    
#     processing_times = {
#         (record["machine"], record["job"]) : record["time"]
#         for record in data["processing"]
#         }
    
#     sequences = [
#         (row[i], row[i+1], j)
#         for j, row in enumerate(data["technology"])
#         for i in range(len(row) - 1) 
#         ]
    
# Model

model = pyo.ConcreteModel()

# Sets and Params

model.M = pyo.RangeSet(0, 9)
model.J = pyo.RangeSet(0, 9)
model.E = pyo.Set(initialize = [(i, j) 
                                for i in model.J 
                                for j in model.J 
                                if i != j])
model.sigma = pyo.Set(initialize = precedences)

model.Big_M = pyo.Param(initialize = sum(pyo.quicksum(pr) for pr in pt))
Big_M = model.Big_M

# Variables

model.x = pyo.Var(model.M, model.J, within = pyo.NonNegativeReals)
x = model.x

model.z = pyo.Var(model.M, model.E, within = pyo.Binary)
z = model.z

model.C = pyo.Var(within = pyo.NonNegativeReals)
C = model.C

# Constraints

# def job_prec_time(model, m, j):
#     if m != model.M.first():
#         m_prev = model.M.prev(m)
#         return x[m_prev, j] + pt[m_prev, j] <= x[m, j]
#     else:
#         return pyo.Constraint.Skip
# model.c1 = pyo.Constraint(model.M, model.J, rule = job_prec_time)

def job_seq_time(model, m1, m2, j):
    return x[m1, j] + pt[j][m1] <= x[m2, j]
model.c1 = pyo.Constraint(model.sigma, rule = job_seq_time)

def prec_cons(model, m, j, k):
    return x[m, j] + pt[j][m] <= x[m, k] + Big_M*(1 - z[m, j, k])
model.c2 = pyo.Constraint(model.M, model.E, rule = prec_cons)

def complimentary_prec_cons(model, m, j, k):
    return z[m, j, k] + z[m, k, j] == 1
model.c3 = pyo.Constraint(model.M, model.E, rule = complimentary_prec_cons)

def total_makespan_cons(model, j):
    m = sequences[j][-1]
    return x[m, j] + pt[j][m] <= C
model.c4 = pyo.Constraint(model.J, rule = total_makespan_cons)

# Objective Function

def obj_fn(model):
    return C
model.obj = pyo.Objective(rule = obj_fn, sense = pyo.minimize)

# Solution

sol = SolverFactory("cplex", executable = path)
sol.options["timelimit"] = 15
res = sol.solve(model)

# Printing the Solution

print(res)














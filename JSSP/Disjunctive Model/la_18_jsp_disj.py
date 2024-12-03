import pyomo.environ as pyo
from pyomo.opt import SolverFactory

path = "F:\\Solvers\\CPLEX_2211\\cplex\\bin\\x64_win64\\cplex.exe"

machining_sequence = []
processing_times = []

with open("la18.txt", "r") as data:
    lines = data.read().splitlines()
    
    for line in lines[1:]:
        mc, pt = [], []
        curr = line.split()
        for i in range(len(curr)):
            if i % 2 == 0:
                mc.append(int(curr[i]))
            else:
                pt.append(int(curr[i]))
        machining_sequence.append(mc)
        processing_times.append(pt)

precedences = [(row[i] + 1, row[i+1] + 1, j+1)
               for j, row in enumerate(machining_sequence)
               for i in range(len(machining_sequence[0]) - 1)]

# Model

model = pyo.ConcreteModel()

# Sets and Params

model.J = pyo.RangeSet(1, len(machining_sequence))
J = model.J

model.M = pyo.RangeSet(1, len(machining_sequence[0]))
M = model.M

model.E = pyo.Set(initialize = [(i, j) 
                                for i in J 
                                for j in J 
                                if i != j])
E = model.E

Big_M = pyo.quicksum([pyo.quicksum(pt) for pt in processing_times])

# Variables

# Start times of different jobs

model.x = pyo.Var(J, M, within = pyo.NonNegativeReals)
x = model.x

"""
Binary variable to check if one job precedes another 
according to the given order
"""

model.z = pyo.Var(E, M, within = pyo.Binary)
z = model.z

model.ms = pyo.Var(within = pyo.NonNegativeReals)
ms = model.ms

# Constraints

def job_seq_time(model, m1, m2, j):
    return x[j, m1] + processing_times[j-1][m1-1] <= x[j, m2]
model.c1 = pyo.Constraint(precedences, rule = job_seq_time)

def prec_cons(model, j, k, m):
    return x[j, m] + processing_times[j-1][m-1] <= x[k, m] + Big_M*(1 - z[j, k, m])
model.c2 = pyo.Constraint(E, M, rule = prec_cons)

def complimentary_prec_cons(model, j, k, m):
    return z[j, k, m] + z[k, j, m] == 1
model.c3 = pyo.Constraint(E, M, rule = complimentary_prec_cons)

def total_makespan_cons(model, j):
    m = machining_sequence[j-1][-1] + 1
    return x[j, m] + processing_times[j-1][m-1] <= ms
model.c4 = pyo.Constraint(J, rule = total_makespan_cons)

# Objective Function

model.obj = pyo.Objective(expr = ms, sense = pyo.minimize)

# Solution

sol = SolverFactory("cplex", executable = path)
sol.options["timelimit"] = 15
res = sol.solve(model)

# Printing the Solution

print(res)







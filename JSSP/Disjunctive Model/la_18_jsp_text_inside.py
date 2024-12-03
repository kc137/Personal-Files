import pyomo.environ as pyo
from pyomo.opt import SolverFactory

path = "F:\\Solvers\\CPLEX_2211\\cplex\\bin\\x64_win64\\cplex.exe"

# Model

model = pyo.ConcreteModel()

# Data

data = """10	10
6	54	0	87	4	48	3	60	7	39	8	35	1	72	5	95	2	66	9	5
3	20	9	46	6	34	5	55	0	97	8	19	4	59	2	21	7	37	1	46
4	45	1	24	8	28	0	28	7	83	6	78	5	23	3	25	9	5	2	73
9	12	1	37	4	38	3	71	8	33	2	12	6	55	0	53	7	87	5	29
3	83	2	49	6	23	9	27	7	65	0	48	4	90	5	7	1	40	8	17
1	66	4	25	0	62	2	84	9	13	6	64	7	46	8	59	5	19	3	85
1	73	3	80	0	41	2	53	9	47	7	57	8	74	4	14	6	67	5	88
5	64	3	84	6	46	1	78	0	84	7	26	8	28	9	52	2	41	4	63
1	11	0	64	7	67	4	85	3	10	5	73	9	38	8	95	6	97	2	17
4	60	8	32	2	95	3	93	1	65	6	85	7	43	9	85	5	46	0	59"""

data = data.split()[2:]

machining_sequence = [[]]
processing_times = [[]]

for i in range(len(data)):
    if i % 2 == 0:
        machining_sequence[-1].append(int(data[i]))
    else:
        processing_times[-1].append(int(data[i]))
    if (i+1) % 20 == 0 and i+1 != 200:
        machining_sequence.append([])
        processing_times.append([])

precedences = [
    (row[i], row[i+1], j) 
    for j, row in enumerate(machining_sequence) 
    for i in range(len(machining_sequence) - 1)
    ]

# Sets

model.jobs = pyo.RangeSet(0, len(machining_sequence) - 1)
jobs = model.jobs

model.mc = pyo.RangeSet(0, len(machining_sequence[0]) - 1)
mc = model.mc

model.e = pyo.Set(initialize = [(p, q) 
                                for p in jobs 
                                for q in jobs 
                                if p != q])
e = model.e

model.sigma = pyo.Set(initialize = precedences)
sigma = model.sigma

big_m = pyo.quicksum([pt[i]  
                      for pt in processing_times 
                      for i in range(len(pt))])

# Variables

model.x = pyo.Var(mc, jobs, within = pyo.NonNegativeReals)
x = model.x

model.z = pyo.Var(mc, e, within = pyo.Binary)
z = model.z

model.c = pyo.Var(within = pyo.NonNegativeReals)
c = model.c

# Constraints

def job_seq_time(model, m1, m2, j):
    return x[m1, j] + processing_times[j][m1] <= x[m2, j]
model.c1 = pyo.Constraint(precedences, rule = job_seq_time)

def prec_cons(model, m, j, k):
    return x[m, j] + processing_times[j][m] <= x[m, k] + big_m*(1 - z[m, j, k])
model.c2 = pyo.Constraint(mc, e, rule = prec_cons)

def comp_prec_cons(model, m, j, k):
    return z[m, j, k] + z[m, k, j] == 1
model.c3 = pyo.Constraint(mc, e, rule = comp_prec_cons)

def max_time_cons(model, j):
    m = machining_sequence[j][-1]
    return x[m, j] + processing_times[j][m] <= c
model.c4 = pyo.Constraint(jobs, rule = max_time_cons)

# Objective Function

def obj_fn(model):
    return c
model.obj = pyo.Objective(rule = obj_fn, sense = pyo.minimize)

# Solution

sol = SolverFactory("cplex")
# sol = SolverFactory("glpk")
# sol = SolverFactory("cplex", executable = path)
sol.options["timelimit"] = 15
res = sol.solve(model)

print(res)




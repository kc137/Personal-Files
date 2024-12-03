import pyomo.environ as pyo
import gurobipy as gp
from pyomo.opt import SolverFactory

acids = [*range(1, 51)]

h_phobic = [2, 4, 5, 6, 11, 12, 17, 20, 21, 25, 27, 28, 30, 31, 33, 37, 44, 46]

# Creating some data to generate the model

list_ij = []

# Indices of Hydrophobic acids that can be matched

for i in h_phobic:
    for j in h_phobic:
        if j > i + 1:
            tp = i, j
            list_ij.append(tp)

ij = gp.tuplelist(list_ij)

list_ik1j, list_ik2j = [], []

for i, j in ij:
    for k in range(i, j):
        if k == (i + j - 1)/2:
            tp = i, j, k
            list_ik2j.append(tp)
        else:
            tp = i, j, k
            list_ik1j.append(tp)

# Incdices for constraints of type-1 and type-2 respectively

ik1j, ik2j = gp.tuplelist(list_ik1j), gp.tuplelist(list_ik2j)

# Matchings that are enables by a folding

list_ijfold = []

for i, j, k in ik2j:
    tp = i, j
    list_ijfold.append(tp)

ijfold = gp.tuplelist(list_ijfold)

# Model

model = pyo.ConcreteModel()

# Variables

# Matching Vars
model.match = pyo.Var(ij, within = pyo.Binary)
match = model.match

# Folding Vars
model.fold = pyo.Var(acids, within = pyo.Binary)
fold = model.fold

# Constraints

def cons_1(model, i, j, k):
    return fold[k] + match[i, j] <= 1
model.c1 = pyo.Constraint(ik1j, rule = cons_1)

def cons_2(model, i, j, k):
    return match[i, j] <= fold[k]
model.c2 = pyo.Constraint(ik2j, rule = cons_2)

# Objective Function

def obj_fn(model):
    return pyo.quicksum(match[i, j] 
                        for i, j in ijfold)
model.obj = pyo.Objective(rule  = obj_fn, sense = pyo.maximize)

# Solution

sol = SolverFactory("cplex")
res = sol.solve(model)

# Printing the Solution

# print(res)

for i, j, k in ik2j:
    if match[i, j]() and match[i, j]() >= 0.9:
        print(f"The aminoacid matching {(i, j)} with folding at aminoacid-{k}")














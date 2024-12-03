import pyomo.environ as pyo, pandas as pd
from pyomo.opt import SolverFactory

model = pyo.ConcreteModel()
N = 5 # Total Cities

# Sets
model.i = pyo.RangeSet(1, 5)
model.j = pyo.RangeSet(1, 5)
model.ii = pyo.RangeSet(2, 5)
model.jj = pyo.RangeSet(2, 5)

# Parameters

C = pd.read_excel("S5P3_Data.xlsx", sheet_name = "TSP", header = 0, index_col = 0, usecols = "A:F", nrows = 5)
# print(C)
# Variables

model.x = pyo.Var(model.i, model.j, domain = pyo.Binary)
x = model.x

model.u = pyo.Var(model.i, domain = pyo.NonNegativeReals)
u = model.u

# Constraints

def Constraint1(model, j):
    return sum(x[i, j] for i in model.i) == 1

model.C1 = pyo.Constraint(model.i, rule = Constraint1)


def Constraint2(model, i):
    return sum(x[i, j] for j in model.j) == 1

model.C2 = pyo.Constraint(model.j, rule = Constraint2)


def Constraint3(model, i, j):
    if i != j:
        return u[i] - u[j] + N*x[i, j] <= N - 1
    else:
        return u[i] - u[i] == 0

model.C3 = pyo.Constraint(model.ii, model.jj, rule = Constraint3)

# Obj Function

def Obj_Fn(model):
    return sum(sum(C[i][j]*x[i, j] for i in model.i) for j in model.j)

model.Obj = pyo.Objective(rule = Obj_Fn, sense = pyo.minimize)

Sol = SolverFactory("couenne", executable = "F:\\Solvers\\couenne\\bin\\couenne.exe")
Res = Sol.solve(model)

for i in model.i:
    for j in model.j:
        if x[i, j]():
            print("Sales man goes from City", i, "to City", j, "and travels", C[i][j], "km")
            
print("Total distance Travelled =", model.Obj())
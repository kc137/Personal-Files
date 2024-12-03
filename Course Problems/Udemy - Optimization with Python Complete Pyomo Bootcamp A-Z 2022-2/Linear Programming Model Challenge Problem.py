import pyomo.environ as pyo
from pyomo.opt import SolverFactory

model = pyo.ConcreteModel()

# Sets

model.i = pyo.RangeSet(1, 3)
model.j = pyo.RangeSet(1, 4)

# Params

model.S = pyo.Param(model.i, initialize = {1 : 35, 2 : 50, 3 : 40})
S = model.S
model.D = pyo.Param(model.j, initialize = {1 : 45, 2 : 20, 3 : 30, 4 : 30})
D = model.D
model.P = pyo.Param(model.i, model.j, initialize = {(1, 1) : 8, (1, 2) : 6, (1, 3) : 10, (1, 4) : 9,
                                                    (2, 1) : 9, (2, 2) : 12, (2, 3) : 13, (2, 4) : 7,
                                                    (3, 1) : 14, (3, 2) : 9, (3, 3) : 16, (3, 4) : 5})
P = model.P

# Vars

model.x = pyo.Var(model.i, model.j, within = pyo.NonNegativeReals)
x = model.x

# Obj Function

def Obj_Fn(model):
	return sum(sum(P[i, j]*x[i, j] for i in model.i) for j in model.j)

model.Obj = pyo.Objective(rule = Obj_Fn, sense = pyo.minimize)

# Constraints

def Constraint1(model, i):
	return sum(x[1, j] for j in model.j) <= S[1]
model.C1 = pyo.Constraint(model.j, rule = Constraint1)

def Constraint2(model, i):
	return sum(x[2, j] for j in model.j) <= S[2]
model.C2 = pyo.Constraint(model.j, rule = Constraint2)

def Constraint3(model, i):
	return sum(x[3, j] for j in model.j) <= S[3]
model.C3 = pyo.Constraint(model.j, rule = Constraint3)

def Constraint4(model, j):
	return sum(x[i, 1] for i in model.i) >= D[1]
model.C4 = pyo.Constraint(model.i, rule = Constraint4)

def Constraint5(model, j):
	return sum(x[i, 2] for i in model.i) >= D[2]
model.C5 = pyo.Constraint(model.i, rule = Constraint5)

def Constraint6(model, j):
	return sum(x[i, 3] for i in model.i) >= D[3]
model.C6 = pyo.Constraint(model.i, rule = Constraint6)

def Constraint7(model, j):
	return sum(x[i, 4] for i in model.i) >= D[4]
model.C7 = pyo.Constraint(model.i, rule = Constraint7)

# Solve

Sol = SolverFactory("couenne", executable = "F:\\Solvers\\couenne\\bin\\couenne.exe")
Res = Sol.solve(model)

print(Res)
print("Obj Function is", model.Obj())
for i in model.i:
    for j in model.j:
        print("Electricity sent from Plant", i, "to City", j, "is", x[i, j]())
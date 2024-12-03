import pyomo.environ as pyo, numpy as np
from pyomo.opt import SolverFactory

model = pyo.ConcreteModel()

# Sets

model.i = pyo.RangeSet(1, 5)

# Parameters

model.hrs = pyo.Param(model.i, initialize = {1 : 6000, 2 : 7000, 3 : 8000, 4 : 9500, 5 : 11000})
hrs = model.hrs

sal_exp = 2000 # Salary for experienced technicians
sal_tr = 1000 # Salary for trainees
hpm = 160 # Hours per month
hrpt = 50 # Hours required per trainee

# Variables

model.x = pyo.Var(model.i, domain = pyo.NonNegativeReals)
x = model.x

model.y = pyo.Var(model.i, domain = pyo.NonNegativeReals)
y = model.y

# Constraints

model.Constraints1 = pyo.ConstraintList()

for i in model.i:
    model.Constraints1.add(hpm*y[i] - hrpt*x[i] >= hrs[i])
    
model.Constraints2 = pyo.ConstraintList()
for i in model.i:
    if i == 1:
        model.Constraints2.add(y[i] == 50)
    else:
        model.Constraints2.add(y[i] == y[i-1] + x[i-1] - 0.05*y[i-1])

# Objective Funtion

def Obj_Fn(model):
    return sum(sal_exp*y[i] + sal_tr*x[i] for i in model.i)
model.Obj = pyo.Objective(rule = Obj_Fn, sense = pyo.minimize)


sol = SolverFactory("couenne")
res = sol.solve(model)

# sol = SolverFactory("mindtpy")
# res = sol.solve(model, mip_solver = "cbc", nlp_solver = "ipopt")

model.pprint()

print("The total labour cost incurred in meeting the service requirements =", model.Obj(), "$")

for i in model.i:
    print("The skilled technicians required for month", i, "will be", y[i]())
for i in model.i:
    print("The trainee technicians required for month", i, "will be", x[i]())
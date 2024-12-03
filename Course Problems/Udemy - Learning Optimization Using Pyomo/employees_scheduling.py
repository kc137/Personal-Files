import pyomo.environ as pyo
from pyomo.opt import SolverFactory

model = pyo.ConcreteModel()

total_req = {'Sunday' : 18,
              'Monday'  : 27,
              'Tuesday'  : 22,
              'Wednesday'  : 26,
              'Thursday'  : 25,              
              'Friday'  : 21,              
              'Saturday'  : 19}

salary =     {'Shift1' : 680,
              'Shift2'  : 705,
              'Shift3'  : 705,
              'Shift4'  : 705,
              'Shift5'  : 705,              
              'Shift6'  : 680,              
              'Shift7'  : 655}

shift_req = {    ('Sunday', 'Shift1'): 0, 
         ('Sunday', 'Shift2'): 1, 
         ('Sunday', 'Shift3'): 1, 
         ('Sunday', 'Shift4'): 1, 
         ('Sunday', 'Shift5'): 1, 
         ('Sunday', 'Shift6'): 1, 
         ('Sunday', 'Shift7'): 0,
         ('Monday', 'Shift1'): 0, 
         ('Monday', 'Shift2'): 0, 
         ('Monday', 'Shift3'): 1, 
         ('Monday', 'Shift4'): 1, 
         ('Monday', 'Shift5'): 1, 
         ('Monday', 'Shift6'): 1, 
         ('Monday', 'Shift7'): 1,
         ('Tuesday', 'Shift1'): 1, 
         ('Tuesday', 'Shift2'): 0, 
         ('Tuesday', 'Shift3'): 0, 
         ('Tuesday', 'Shift4'): 1, 
         ('Tuesday', 'Shift5'): 1, 
         ('Tuesday', 'Shift6'): 1, 
         ('Tuesday', 'Shift7'): 1,
         ('Wednesday', 'Shift1'): 1, 
         ('Wednesday', 'Shift2'): 1, 
         ('Wednesday', 'Shift3'): 0, 
         ('Wednesday', 'Shift4'): 0, 
         ('Wednesday', 'Shift5'): 1, 
         ('Wednesday', 'Shift6'): 1, 
         ('Wednesday', 'Shift7'): 1,
         ('Thursday', 'Shift1'): 1, 
         ('Thursday', 'Shift2'): 1, 
         ('Thursday', 'Shift3'): 1, 
         ('Thursday', 'Shift4'): 0, 
         ('Thursday', 'Shift5'): 0, 
         ('Thursday', 'Shift6'): 1, 
         ('Thursday', 'Shift7'): 1,
         ('Friday', 'Shift1'): 1, 
         ('Friday', 'Shift2'): 1, 
         ('Friday', 'Shift3'): 1, 
         ('Friday', 'Shift4'): 1, 
         ('Friday', 'Shift5'): 0, 
         ('Friday', 'Shift6'): 0, 
         ('Friday', 'Shift7'): 1,
         ('Saturday', 'Shift1'): 1, 
         ('Saturday', 'Shift2'): 1, 
         ('Saturday', 'Shift3'): 1, 
         ('Saturday', 'Shift4'): 1, 
         ('Saturday', 'Shift5'): 1, 
         ('Saturday', 'Shift6'): 0, 
         ('Saturday', 'Shift7'): 0}

# Sets

model.days = pyo.Set(initialize = ['Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday'], 
                     name = "Days")
model.shifts = pyo.Set(initialize = ['Shift1', 'Shift2', 'Shift3', 'Shift4', 'Shift5', 'Shift6', 'Shift7'], 
                       name = "Shifts")

# Params

model.total_workers_req = pyo.Param(model.days, within = pyo.Any, 
                                  initialize = total_req)
model.salary = pyo.Param(model.shifts, within = pyo.Any, 
                         initialize = salary)

# Variables

model.x = pyo.Var(model.shifts, within = pyo.NonNegativeIntegers)
x = model.x

# Constraints

def workers(model, i):
    return sum(x[j]*shift_req[i, j] for j in model.shifts) >= model.total_workers_req[i]
model.workers_req = pyo.Constraint(model.days, rule = workers)

# Objective Function

def obj_fn(model):
    return sum(x[i]*model.salary[i] for i in model.shifts)
model.obj = pyo.Objective(rule = obj_fn)

# Solution

sol = SolverFactory("cplex")
res = sol.solve(model)

for shift in x:
    print(f"{x[shift]} = {x[shift]()}")
    
print(f"Total Cost : {model.obj()}")
















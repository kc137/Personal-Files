import pyomo.environ as pyo, gurobipy as gp, pandas as pd, matplotlib, \
    matplotlib.pyplot as plt
from pyomo.opt import SolverFactory

# Sets and Parameters

# Number of workers required for each shift

shifts, shiftRequirements = gp.multidict({
  "Mon1":  3,
  "Tue2":  2,
  "Wed3":  4,
  "Thu4":  4,
  "Fri5":  5,
  "Sat6":  6,
  "Sun7":  5,
  "Mon8":  2,
  "Tue9":  2,
  "Wed10": 3,
  "Thu11": 4,
  "Fri12": 6,
  "Sat13": 7,
  "Sun14": 5 })

# Amount each worker is paid to work 1-shift

workers, pay = gp.multidict({
  "Amy":   10,
  "Bob":   12,
  "Cathy": 10,
  "Dan":   8,
  "Ed":    8,
  "Fred":  9,
  "Gu":    11 })

# Worker availability

availability = gp.tuplelist([
('Amy', 'Tue2'), ('Amy', 'Wed3'), ('Amy', 'Fri5'), ('Amy', 'Sun7'),
('Amy', 'Tue9'), ('Amy', 'Wed10'), ('Amy', 'Thu11'), ('Amy', 'Fri12'),
('Amy', 'Sat13'), ('Amy', 'Sun14'), ('Bob', 'Mon1'), ('Bob', 'Tue2'),
('Bob', 'Fri5'), ('Bob', 'Sat6'), ('Bob', 'Mon8'), ('Bob', 'Thu11'),
('Bob', 'Sat13'), ('Cathy', 'Wed3'), ('Cathy', 'Thu4'), ('Cathy', 'Fri5'),
('Cathy', 'Sun7'), ('Cathy', 'Mon8'), ('Cathy', 'Tue9'), ('Cathy', 'Wed10'),
('Cathy', 'Thu11'), ('Cathy', 'Fri12'), ('Cathy', 'Sat13'),
('Cathy', 'Sun14'), ('Dan', 'Tue2'), ('Dan', 'Wed3'), ('Dan', 'Fri5'),
('Dan', 'Sat6'), ('Dan', 'Mon8'), ('Dan', 'Tue9'), ('Dan', 'Wed10'),
('Dan', 'Thu11'), ('Dan', 'Fri12'), ('Dan', 'Sat13'), ('Dan', 'Sun14'),
('Ed', 'Mon1'), ('Ed', 'Tue2'), ('Ed', 'Wed3'), ('Ed', 'Thu4'),
('Ed', 'Fri5'), ('Ed', 'Sun7'), ('Ed', 'Mon8'), ('Ed', 'Tue9'),
('Ed', 'Thu11'), ('Ed', 'Sat13'), ('Ed', 'Sun14'), ('Fred', 'Mon1'),
('Fred', 'Tue2'), ('Fred', 'Wed3'), ('Fred', 'Sat6'), ('Fred', 'Mon8'),
('Fred', 'Tue9'), ('Fred', 'Fri12'), ('Fred', 'Sat13'), ('Fred', 'Sun14'),
('Gu', 'Mon1'), ('Gu', 'Tue2'), ('Gu', 'Wed3'), ('Gu', 'Fri5'),
('Gu', 'Sat6'), ('Gu', 'Sun7'), ('Gu', 'Mon8'), ('Gu', 'Tue9'),
('Gu', 'Wed10'), ('Gu', 'Thu11'), ('Gu', 'Fri12'), ('Gu', 'Sat13'),
('Gu', 'Sun14')
])

def mo_model():
    # Model
    
    model = pyo.ConcreteModel()
    
    # Variables 
    
    # Decision Variables
    
    # Initialize assignment decision varaibles
    model.x = pyo.Var(availability, within = pyo.Binary)
    x = model.x
    
    # Determines the number of exrta workers required
    model.slacks = pyo.Var(shifts, within = pyo.NonNegativeIntegers)
    slacks = model.slacks
    
    # Auxiliary Variables (Derived from decision variables)
    
    model.totSlack = pyo.Var(within = pyo.NonNegativeIntegers)
    totSlack = model.totSlack
    
    # Total shifts worked by each employed worker
    model.totShifts = pyo.Var(workers, within = pyo.NonNegativeIntegers)
    totShifts = model.totShifts
    
    # Min Shifts
    model.minShifts = pyo.Var(within = pyo.NonNegativeIntegers)
    minShifts = model.minShifts
    
    # Max Shifts
    model.maxShifts = pyo.Var(within = pyo.NonNegativeIntegers)
    maxShifts = model.maxShifts
    
    # Constraints
    
    # All shifts requirements must be satisfied
    
    def shift_req(model, s):
        return (pyo.quicksum(x[w, s] for w, s1 in availability if s1 == s) 
                + slacks[s] 
                == 
                shiftRequirements[s])
    model.c1 = pyo.Constraint(shifts, rule = shift_req)
    
    # Total extra workers equal to totSlack
    
    def extra_workers(model):
        return pyo.quicksum(slacks[s] for s in shifts) == totSlack
    model.c2 = pyo.Constraint(rule = extra_workers)
    
    # Total number of shifts for each worker
    
    def tot_shifts(model, w):
        return pyo.quicksum(x[w, s] for w1, s in availability if w1 == w) == totShifts[w]
    model.c3 = pyo.Constraint(workers, rule = tot_shifts)
    
    # Min and Max Constraints
    
    model.min_max = pyo.ConstraintList()
    
    for w in workers:
        model.min_max.add(minShifts <= totShifts[w])
        model.min_max.add(maxShifts >= totShifts[w])
    
    # Objective Function
    
    model.obj_list = pyo.ObjectiveList()
    
    def obj_fn(model):
        return totSlack + (maxShifts - minShifts)
    
    def obj_fn_2(model):
        return pyo.quicksum(totShifts[w] for w in workers)
    
    model.obj_list.add(expr = obj_fn(model), sense = pyo.minimize)
    model.obj_list.add(expr = obj_fn_2(model), sense = pyo.minimize)
    
    for o in range(len(model.obj_list)):
        model.obj_list[o + 1].deactivate()
    
    # sol = SolverFactory("cplex")
    # res = sol.solve(model)
    # print(res)
    return model

from pyaugmecon import PyAugmecon

new_model = mo_model()

options = {
    "name" : "mo_model", 
    # "solver_name" : "glpk", 
    "grid_points" : 5, 
    "process_timeout" : 5
    }

py_augmecon = PyAugmecon(new_model, options)
py_augmecon.solve()



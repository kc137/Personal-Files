import pyomo.environ as pyo, numpy as np, pandas as pd, gurobipy as gp
from pyomo.opt import SolverFactory
from pyomo.util.infeasible import log_infeasible_constraints

# Parameters

years = [1, 2, 3]
skills = ['s1', 's2', 's3']

curr_workforce = {'s1': 2000, 's2': 1500, 's3': 1000}
demand = {
    (1, 's1'): 1000,
    (1, 's2'): 1400,
    (1, 's3'): 1000,
    (2, 's1'): 500,
    (2, 's2'): 2000,
    (2, 's3'): 1500,
    (3, 's1'): 0,
    (3, 's2'): 2500,
    (3, 's3'): 2000
}

rookie_attrition = {'s1': 0.25, 's2': 0.20, 's3': 0.10}
veteran_attrition = {'s1': 0.10, 's2': 0.05, 's3': 0.05}
demoted_attrition = 0.5
max_hiring = {
    (1, 's1'): 500,
    (1, 's2'): 800,
    (1, 's3'): 500,
    (2, 's1'): 500,
    (2, 's2'): 800,
    (2, 's3'): 500,
    (3, 's1'): 500,
    (3, 's2'): 800,
    (3, 's3'): 500
}

max_overmanning = 150
max_parttime = 50
parttime_cap = 0.5
max_train_unskilled = 200
max_train_semiskilled = 0.25

training_cost = {'s1': 400, 's2': 500}
layoff_cost = {'s1': 200, 's2': 500, 's3': 500}
parttime_cost = {'s1': 500, 's2': 400, 's3': 400}
overmanning_cost = {'s1': 1500, 's2': 2000, 's3': 3000}

# Model

model = pyo.ConcreteModel()

model.hire = pyo.Var(years, skills, within = pyo.NonNegativeReals)
hire = model.hire

model.part_time = pyo.Var(years, skills, within = pyo.NonNegativeReals, 
                          bounds = (0, max_parttime))
part_time = model.part_time

model.workforce = pyo.Var(years, skills, within = pyo.NonNegativeReals)
workforce = model.workforce

model.layoff = pyo.Var(years, skills, within = pyo.NonNegativeReals)
layoff = model.layoff

model.excess = pyo.Var(years, skills, within = pyo.NonNegativeReals)
excess = model.excess

model.train = pyo.Var(years, skills, skills, within = pyo.NonNegativeReals)
train = model.train

# Constraints

model.hire_ub = pyo.ConstraintList()

def hire_ub(model, t, s):
    return (0, hire[t, s], max_hiring[t, s])
model.hire_ub_cons = pyo.Constraint(years, skills, rule = hire_ub)

"""
Initial Balance: Workforce  s  available in year  t=1  is equal to the workforce 
of the previous year, recent hires, promoted and demoted workers 
(after accounting for attrition), minus layoffs and transferred workers.

For t > 1 :
Balance: Workforce  s  available in year  t>1  is equal to the workforce of 
the previous year, recent hires, promoted and demoted workers 
(after accounting for attrition), minus layoffs and transferred workers.
"""

"""
return workforce[t, s] == ((1 - veteran_attrition[s])*(curr_workforce[s] if t == 1 else workforce[t-1, s]) 
        + (1 - rookie_attrition[s])*hire[t, s] 
        + pyo.quicksum((1 - veteran_attrition[s])*train[t, s2, s] 
                       - train[t, s, s2] 
                       for s2 in skills 
                       if s2 < s) 
        + pyo.quicksum((1 - demoted_attrition)*train[t, s2, s] 
                       - train[t, s, s2] 
                       for s2 in skills 
                       if s2 > s) 
        - layoff[t, s])
"""

def initial_balance(model, t, s):
    if t == 1:
        return (workforce[t, s] == (1 - veteran_attrition[s])*(curr_workforce[s]) 
                + (1 - rookie_attrition[s])*hire[t, s] 
                + pyo.quicksum((1 - veteran_attrition[s])*train[t, s2, s] 
                               - train[t, s, s2] 
                               for s2 in skills 
                               if s2 < s) 
                + pyo.quicksum((1 - demoted_attrition)*train[t, s2, s] 
                               - train[t, s, s2] 
                               for s2 in skills 
                               if s2 > s) 
                - layoff[t, s])
    else:
        return (workforce[t, s] == (1 - veteran_attrition[s])*(workforce[t-1, s]) 
                + (1 - rookie_attrition[s])*hire[t, s] 
                + pyo.quicksum((1 - veteran_attrition[s])*train[t, s2, s] 
                               - train[t, s, s2] 
                               for s2 in skills 
                               if s2 < s) 
                + pyo.quicksum((1 - demoted_attrition)*train[t, s2, s] 
                               - train[t, s, s2] 
                               for s2 in skills 
                               if s2 > s) 
                - layoff[t, s])
model.c1 = pyo.Constraint(years, skills, rule = initial_balance)

"""
Unskilled Training

The Unskilled training constraints force that per year only 200 workers can be 
retrained from Unskilled to Semi-skilled due to capacity limitations. 
Also, no one can be trained in one year from Unskilled to Skilled.
"""

def unskilled_training(model, t, s):
    if s == "s1":
        return pyo.Constraint.Skip
    elif s == "s2":
        return train[t, "s1", s] <= max_train_unskilled
    else:
        return train[t, "s1", s] == 0
model.c2 = pyo.Constraint(years, skills, rule = unskilled_training)

"""
Semi-skilled Training

The Semi-skilled training states that the retraining of Semi-skilled workers 
to skilled workers is limited to no more than one quarter of the skilled labor 
force at this time. This is due to capacity limitations.
"""

model.semi_skilled_cons = pyo.ConstraintList()

for t in years:
    model.semi_skilled_cons.add(
        train[t, "s2", "s3"] <= max_train_semiskilled*workforce[t, "s3"]
        )

"""
Overmanning

The overmanning constraints ensure that the total overmanning over 
all skill levels in one year is no more than 150.
"""

def overmanning(model, t):
    return pyo.quicksum(excess[t, s] for s in skills) <= max_overmanning
model.c4 = pyo.Constraint(years, rule = overmanning)

"""
Demand

The demand constraints ensure that the number of workers of each level and 
year equals the required number of workers plus the Overmanned workers and 
the number of workers who are working part-time.
"""

def demand_cons(model, t, s):
    return (workforce[t, s] == 
            demand[t, s] + excess[t, s] + parttime_cap*part_time[t, s]) 
model.c5 = pyo.Constraint(years, skills, rule = demand_cons)

# Objective Function

def obj_fn(model):
    return pyo.quicksum(layoff[t, s] 
                        for t in years 
                        for s in skills)
model.obj = pyo.Objective(rule = obj_fn, sense = pyo.minimize)

# Solution

sol = SolverFactory("cplex")
res = sol.solve(model)

# Printing the Solution

print(res)

log_infeasible_constraints(model)

"""
Finally Solved...

Problem: 
- Name: tmpe7fp9k5f
  Lower bound: 841.796875
  Upper bound: 841.796875
  Number of objectives: 1
  Number of constraints: 48
  Number of variables: 63
  Number of nonzeros: 135
  Sense: minimize
Solver: 
- Status: ok
  User time: 0.23
  Termination condition: optimal
  Termination message: Dual simplex - Optimal\x3a Objective = 8.4179687500e+02
  Error rc: 0
  Time: 0.4317362308502197
Solution: 
- number of solutions: 0
  number of solutions displayed: 0
"""





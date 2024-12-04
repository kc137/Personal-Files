import pyomo.environ as pyo, logging
from pyomo.opt import SolverFactory
from pyomo.util.infeasible import log_infeasible_constraints
from data import NC, ND, NV, coords, demands, time_windows, service_time, \
    max_dur, Q, distance_matrix

M = 1000

# Model

model = pyo.ConcreteModel()

# Sets and Params

model.N = pyo.RangeSet(1, NC + ND)
model.C = pyo.RangeSet(1, NC)
model.D = pyo.RangeSet(NC+1, NC+ND)
model.V = pyo.RangeSet(1, NV)

# Variables

x_var_list = [(i, j, k) 
              for i in model.N 
              for j in model.N 
              for k in model.V 
              if i != j]

model.x = pyo.Var(x_var_list, within = pyo.Binary)
x = model.x

model.y = pyo.Var(model.D, model.N, model.V, within = pyo.Binary)
y = model.y

model.z = pyo.Var(model.N, model.D, model.V, within = pyo.Binary)
z = model.z

model.s = pyo.Var(model.N, model.V, within = pyo.NonNegativeReals)
s = model.s

# Constraints

"""
An arc cannot be travelled by a vehicle, unless this vehicle starts from the single depot 
and it causes a customer to be at the beginning of the route after a depot or after the other 
customer
"""

def visit_once_arc(model, i):
    return (pyo.quicksum(x[j, i, k] 
                        for j in model.C 
                        for k in model.V
                        if j != i) 
            + pyo.quicksum(y[d, i, k] 
                           for d in model.D 
                           for k in model.V 
                           if i != d)) == 1
model.c1 = pyo.Constraint(model.N, rule = visit_once_arc)

"""
Route consists of the route of customer to the other customer and 
customer to the depot i.e. each customer can either link to a depot or a customer.
"""

def cust_to_point(model, i):
    return (pyo.quicksum(x[i, j, k] 
                        for j in model.C 
                        for k in model.V
                        if i != j) 
            + pyo.quicksum(z[i, d, k] 
                           for d in model.D 
                           for k in model.V 
                           if i != d)) == 1
model.c2 = pyo.Constraint(model.N, rule = cust_to_point)

"""
Below is related to the start and finish of each 
route and certify that each route starts from the single depot and 
finishes at the single depot.
"""

def start_to_finish(model, k):
    return (pyo.quicksum(y[d, i, k] 
                         for d in model.D 
                         for i in model.C) 
            == pyo.quicksum(z[j, d, k] 
                   for j in model.C 
                   for d in model.D))
model.c3 = pyo.Constraint(model.V, rule = start_to_finish)

"""
Below implies that the input and output of the customers are equal and each 
customer receives services once.
"""

def flow_cons(model, i, k):
    return (pyo.quicksum(x[i, j, k] 
                         for j in model.C 
                         if i != j) 
            + pyo.quicksum(z[i, d, k] 
                           for d in model.D 
                           if i != d) 
            == pyo.quicksum(x[j, i, k] 
                            for j in model.C 
                            if i != j) 
            + pyo.quicksum(y[d, i, k] 
                           for d in model.D 
                           if i != d))
model.c4 = pyo.Constraint(model.N, model.V, rule = flow_cons)

"""
Below ensures that an arc cannot be travelled by the vehicle unless this 
vehicle starts from the single depot.
"""

def start_arc_cons(model, k):
    return (pyo.quicksum(x[i, j, k] 
                         for i in model.C 
                         for j in model.C
                         if i != j) 
            <= M*pyo.quicksum(y[d, i, k] 
                           for d in model.D 
                           for i in model.C))
model.c5 = pyo.Constraint(model.V, rule = start_arc_cons)

"""
Below is related to the capacity of each vehicle in such a way that the total 
demands of the customers don’t violate the capacity of the vehicle.
"""

def demand_cons(model, k):
    return (pyo.quicksum(y[d, i, k]*demands[i-1] 
                         for d in model.D 
                         for i in model.C) 
            + pyo.quicksum(x[i, j, k]*demands[j-1] 
                                 for i in model.C 
                                 for j in model.C 
                                 if i != j)) <= Q
model.c6 = pyo.Constraint(model.V, rule = demand_cons)

model.time_cons = pyo.ConstraintList()

for i in model.C:
    for j in model.C:
        for k in model.V:
            if i != j:
                model.time_cons.add(
                    s[i, k] + service_time[i-1] + distance_matrix[i-1][j-1] <= s[j, k] + M*(1 - x[i, j, k]) + 0.001
                    )

def time_bound_cons_1(model, i, j, k):
    if i != j:
        return time_windows[i-1][0]*x[i, j, k] <= s[i, k]
    else:
        return pyo.Constraint.Skip
model.c8 = pyo.Constraint(model.C, model.C, model.V, rule = time_bound_cons_1)

def time_bound_cons_2(model, i, j, k):
    if i != j:
        return s[i, k] <= time_windows[i-1][1]*x[i, j, k]
    else:
        return pyo.Constraint.Skip
model.c9 = pyo.Constraint(model.C, model.C, model.V, rule = time_bound_cons_2)

def depot_time_cons(model, d, k):
    return s[d, k] == 0
model.c10 = pyo.Constraint(model.D, model.V, rule = depot_time_cons)

def max_duration_cons(model, k):
    return pyo.quicksum(distance_matrix[i-1][j-1]*x[i, j, k] 
                        for i in model.C 
                        for j in model.C 
                        if i != j) <= max_dur
model.c11 = pyo.Constraint(model.V, rule = max_duration_cons)

# Objective Function

def obj_fn(model):
    return pyo.quicksum(x[i, j, k]*distance_matrix[i-1][j-1] 
                        for i in model.N 
                        for j in model.N 
                        for k in model.V 
                        if i != j)
model.obj = pyo.Objective(rule = obj_fn, sense = pyo.minimize)

# Solution

sol = SolverFactory("cplex")
sol.options["timelimit"] = 15
res = sol.solve(model)

# Printing the Solution

print(res)

# print(f"The total distance covered by all vehicles in MDVRPTW : {model.obj()}")

"""
import logging
from pyomo.util.infeasible import log_infeasible_constraints

def log_pyomo_infeasible_constraints(model_instance):          
    # Create a logger object with DEBUG level
    logging_logger = logging.getLogger()
    logging_logger.setLevel(logging.DEBUG)
    # Create a console handler
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    # add the handler to the logger
    logging_logger.addHandler(ch)
    # Log the infeasible constraints of pyomo object
    print("Displaying Infeasible Constraints")
    log_infeasible_constraints(model_instance, log_expression=True,
                         log_variables=True, logger=logging_logger)
"""











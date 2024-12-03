import pyomo.environ as pyo
from pyomo.opt import SolverFactory
from crews_1_data import unique_arcs, lang_score_dict, flight_score_dict, lang_dict, flight_dict

# Model

model = pyo.ConcreteModel()

# Sets and Params

model.pilots = pyo.RangeSet(1, 8)
pilots = model.pilots

# Variables

model.fly = pyo.Var(flight_score_dict, within = pyo.Binary)
fly = model.fly

# Constraints

def at_most_one_flight(model, p):
    return pyo.quicksum(fly[a, b] 
                        for a, b in flight_score_dict 
                        if a == p or b == p) <= 1
model.c1 = pyo.Constraint(pilots, rule = at_most_one_flight)

# Objective Function

def obj_fn(model):
    return pyo.quicksum(flight_score_dict[a, b][1]*fly[a, b] 
                        for a, b in flight_score_dict)
model.obj = pyo.Objective(rule = obj_fn, sense = pyo.maximize)

# Solution

sol = SolverFactory("cplex")
res = sol.solve(model)

# Printing the Results

print(res)

for a, b in flight_score_dict:
    if fly[a, b]() and fly[a, b]() >= 0.9:
        f_type = flight_dict[flight_score_dict[a, b][0]]
        l_type = lang_dict[lang_score_dict[a, b][0]]
        print(f"Pair of Crew-{a, b} is included for flight type-{f_type} with {l_type} language.")
import pyomo.environ as pyo, gurobipy as gp, math
from pyomo.opt import SolverFactory

M = 1e9

# Model

model = pyo.ConcreteModel()

# Sets and Parameters

model.c = pyo.Set(initialize = [*range(1, 10)])
model.f = pyo.Set(initialize = [*range(1, 24)])
model.e = pyo.RangeSet(1, 14)
model.t = pyo.RangeSet(15, 23)

counties, c_coords, forecast  = gp.multidict({
    1: [(1, 1.5), 351],
    2: [(3, 1), 230],
    3: [(5.5, 1.5), 529],
    4: [(1, 4.5 ), 339],
    5: [(3, 3.5), 360],
    6: [(5.5, 4.5), 527],
    7: [(1, 8), 469],
    8: [(3, 6), 234],
    9: [(4.5, 8), 500]   
})

for c in model.c:
    forecast[c] = round(1.2*forecast[c])

existing, e_coords, e_cap  = gp.multidict({
        1: [(1, 2), 281],
        2: [(2.5, 1), 187],
        3: [(5, 1), 200],
        4: [(6.5, 3.5), 223],
        5: [(1, 5), 281],
        6: [(3, 4), 281],
        7: [(5, 4), 222],
        8: [(6.5, 5.5), 200],
        9: [(1, 8.5), 250], 
        10: [(1.5, 9.5), 125],
        11: [(8.5, 6), 187],
        12: [(5, 8), 300],
        13: [(3, 9), 300],
        14: [(6, 9), 243]
    })

temp, t_coords, t_cap = gp.multidict({
        15: [(1.5, 1), 100],
        16: [(3.5, 1.5), 100],
        17: [(5.5, 2.5), 100],
        18: [(1.5, 3.5), 100],
        19: [(3.5, 2.5), 100],
        20: [(4.5, 4.5), 100],
        21: [(1.5, 6.5), 100],
        22: [(3.5, 6.5), 100],
        23: [(5.5, 6.5), 100]
    })

d_cost = 5
tf_cost = 500e3

f_coords = {}

for e in e_coords:
    f_coords[e] = e_coords[e]

for t in t_coords:
    f_coords[t] = t_coords[t]

def calculate_distance(loc1, loc2):
    return math.hypot(loc1[0] - loc2[0], loc1[1] - loc2[1])

distance_matrix = {(c, f) : calculate_distance(c_coords[c], f_coords[f]) 
                   for c in model.c 
                   for f in model.f}

# Variables

model.y = pyo.Var(model.t, within = pyo.Binary)
y = model.y

model.x = pyo.Var(model.c, model.f, within = pyo.NonNegativeReals)
x = model.x

model.z = pyo.Var(model.t, within = pyo.NonNegativeIntegers)
z = model.z

# Constraints

def demand(model, c):
    return pyo.quicksum(x[c, f] for f in model.f) == forecast[c]
model.c1 = pyo.Constraint(model.c, rule = demand)

def existing_facilities_capacity(model, e):
    return pyo.quicksum(x[c, e] for c in model.c) <= e_cap[e]
model.c2 = pyo.Constraint(model.e, rule = existing_facilities_capacity)

def temp_facilities_capacity(model, t):
    return pyo.quicksum(x[c, t] for c in model.c) <= t_cap[t]*y[t] + z[t]
model.c3 = pyo.Constraint(model.t, rule = temp_facilities_capacity)

# Objective Function

def obj_fn(model):
    return (pyo.quicksum(x[c, f]*d_cost*distance_matrix[c, f] 
                         for c in model.c 
                         for f in model.f) + 
            pyo.quicksum(y[t]*tf_cost for t in model.t) + 
            M*(pyo.quicksum(z[t] for t in model.t)))
model.obj = pyo.Objective(rule = obj_fn, sense = pyo.minimize)

# Solution

sol = SolverFactory("cplex")
res = sol.solve(model)

# Printing the Solution

for t in model.t:
    if y[t]() and y[t]() >= 0.9:
        print(f"The temporary facility is built at Location-{t}")

temp_facility_cost = sum(y[t]()*tf_cost for t in model.t)
print(f"Total cost of buillding the temporary facilites : ${temp_facility_cost}")

patient_allocation_cost = round(d_cost*sum(x[c, f]()*distance_matrix[c, f] 
                         for c in model.c 
                         for f in model.f), 3)
print(f"Total cost for alloting the patients to the facilities : ${patient_allocation_cost}")

print(f"The total cost for the COVID-19 Facility Location Problem : ${round(model.obj(), 3)}.")

f_demand = {}

for f in model.f:
    temp = 0
    for c in model.c:
        allocations = round(x[c, f]())
        if allocations:
            print(f"Number of COVID-19 patients from county {c} are treated at facility {f} : {allocations}")
        temp += allocations
    f_demand[f] = temp
    print(f"Total number of COVID-19 patients that are treated at facility {f} : {temp}")

total_demand = 0
    
for c in model.c:
    total_demand += forecast[c]
    
demand_satisfied = 0
for f in model.f:
    demand_satisfied += f_demand[f]
    
print(f"Total demand of patients : {total_demand} patients")
print(f"Demand satisfied / Beds allocated : {demand_satisfied}")

for t in model.t:
    if z[t]() and z[t]() >= 0.9:
        print(f"Extra capacity at Facility-{t} : {z[t]()}-Beds installed.")
    
"""
Reference :
[1] Katherine Klise and Michael Bynum. Facility Location Optimization Model for COVID-19 Resources. April 2020. Joint DOE Laboratory Pandemic Modeling and Analysis Capability. SAND2020-4693R.
"""


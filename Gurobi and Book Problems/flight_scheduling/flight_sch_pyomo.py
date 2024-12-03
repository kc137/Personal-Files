import pyomo.environ as pyo
from pyomo.opt import SolverFactory

path = "F:\\Solvers\\CPLEX_2211\\cplex\\bin\\x64_win64\\cplex.exe"

flights_dict = {}
cities_set = set()
destination = "FCO"

with open("flights.txt") as data:
    lines = data.read().splitlines()
    
    for line in lines:
        plan = line.split(",")
        origin, dest, dept_time, arri_time, price = plan
        flights_dict.setdefault((origin, dest), [])
        
        flights_dict[(origin, dest)].append((dept_time, arri_time, int(price)))
        if origin != "FCO":
            cities_set.add(origin)

# Model

model = pyo.ConcreteModel()

# Sets and Params

model.cities = pyo.Set(initialize = list(cities_set))
cities = model.cities

model.flights = pyo.Set(initialize = flights_dict.keys())
flights = model.flights

model.count = pyo.RangeSet(1, 10)
count = model.count

# Variables

model.x = pyo.Var(flights, count, within = pyo.Binary)
x = model.x

# Constraints

model.once = pyo.ConstraintList()

for ori, dest in flights_dict:
    model.once.add(
        pyo.quicksum(x[ori, dest, c] for c in count) == 1
        )

# Objective Function

def obj_fn(model):
    return pyo.quicksum(
        x[o, d, c]*flights_dict[o, d][c-1][2] 
        for o, d in flights 
        for c in count 
        )
model.obj = pyo.Objective(rule = obj_fn, sense = pyo.minimize)

# Solution

sol = SolverFactory("cplex", executable = path)
res = sol.solve(model)

# Printing the Solution

print(res)

for o, d in flights:
    for c in count:
        if x[o, d, c]() and x[o, d, c]() >= 0.9:
            price = flights_dict[o, d][c-1][2]
            print(f"Flight scheduled from {o} to {d} with a ticket of {price}$.")


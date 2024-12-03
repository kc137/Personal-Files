import pyomo.environ as pyo
from pyomo.opt import SolverFactory

CAP = 1500

model = pyo.ConcreteModel()

# Sets and Params

model.clients = pyo.RangeSet(1, 7)

qty_list = [12, 31, 20, 25, 50, 40, 60]

lot_size_list = [10, 8, 6, 9, 15, 10, 12]

price_per_lot_list = [1000, 600, 600, 800, 1200, 800, 1100]

transport_cost_list = [80, 70, 85, 80, 73, 70, 80]

model.quantities = pyo.Param(model.clients, within = pyo.Any, 
                             initialize = {
                                 c : qty_list[c-1] for c in model.clients
                                 })

model.lot_sizes = pyo.Param(model.clients, within = pyo.Any, 
                             initialize = {
                                 c : lot_size_list[c-1] for c in model.clients
                                 })

model.prices = pyo.Param(model.clients, within = pyo.Any, 
                             initialize = {
                                 c : price_per_lot_list[c-1] for c in model.clients
                                 })

model.transport_cost = pyo.Param(model.clients, within = pyo.Any, 
                             initialize = {
                                 c : transport_cost_list[c-1] for c in model.clients
                                 })

# Variables

model.lots = pyo.Var(model.clients, within = pyo.NonNegativeIntegers)
lots = model.lots

# Constraints

def capacity(model):
    return sum(model.lot_sizes[c]*lots[c] for c in model.clients) <= CAP
model.c1 = pyo.Constraint(rule = capacity)

def lots_cons(model, c):
    return lots[c] <= model.quantities[c]
model.c2 = pyo.Constraint(model.clients, rule = lots_cons)

# Objective Function

def obj_fn(model):
    return sum((model.prices[c] - model.transport_cost[c]*model.lot_sizes[c])*lots[c] 
               for c in model.clients)
model.obj = pyo.Objective(rule = obj_fn, sense = pyo.maximize)

# Solution

sol = SolverFactory("cplex")
res = sol.solve(model)

print(res)

for c in model.clients:
    print(f"Lots from Client-{c} : {lots[c]()}")


import pyomo.environ as pyo
from pyomo.opt import SolverFactory

model = pyo.ConcreteModel()

selling_price_reg = 12
selling_price_extra = 14

oils = {1 : "National", 2 : "Imported"}
gasolines = {1 : "Regular", 2 : "Extra"}

with open("product_mixing.txt", "r") as data:
    lines = data.read().splitlines()
    
    line_1 = lines[1].strip().split()
    max_sp_reg = int(line_1[1])
    min_or_reg = int(line_1[2])
    max_dem_reg, min_dem_reg = int(line_1[3]), int(line_1[4])
    
    line_2 = lines[2].strip().split()
    max_sp_extra = int(line_2[1])
    min_or_extra = int(line_2[2])
    max_dem_extra, min_dem_extra = int(line_2[3]), int(line_2[4])
    
    line_5 = lines[5].strip().split()
    sp_national = int(line_5[1])
    or_national = int(line_5[2])
    inv_national = int(line_5[3])
    cost_national = int(line_5[4])
    
    line_6 = lines[6].strip().split()
    sp_imported = int(line_6[1])
    or_imported = int(line_6[2])
    inv_imported = int(line_6[3])
    cost_imported = int(line_6[4])
    

# Sets and Parameters

model.gasoline = pyo.RangeSet(1, 2)
model.oil = pyo.RangeSet(1, 2)

pressures_list = [sp_national, sp_imported]
model.sp = pyo.Param(model.gasoline, within = pyo.Any, 
                     initialize = {
                         gas : pressures_list[gas-1] 
                         for gas in model.gasoline
                         })
sp = model.sp

octane_list = [or_national, or_imported]
model.octane = pyo.Param(model.gasoline, within = pyo.Any, 
                         initialize = {
                             gas : octane_list[gas-1] 
                             for gas in model.gasoline
                             })
octane = model.octane

# Variables

model.x = pyo.Var(model.oil, model.gasoline, within = pyo.NonNegativeReals, 
                  bounds = (0, None))
x = model.x

# Constraints

def steam_pressure_1(model):
    return sum(sp[o]*x[o, 1] for o in model.oil) <= max_sp_reg*sum(x[o, 1] for o in model.oil)
model.c1 = pyo.Constraint(rule = steam_pressure_1)

def steam_pressure_2(model):
    return sum(sp[o]*x[o, 2] for o in model.oil) <= max_sp_extra*sum(x[o, 2] for o in model.oil)
model.c2 = pyo.Constraint(rule = steam_pressure_2)

model.octane_rating_cons = pyo.ConstraintList()

model.octane_rating_cons.add(
    sum(octane[o]*x[o, 1] for o in model.oil) >= min_or_reg*sum(x[o, 1] for o in model.oil)
    )
model.octane_rating_cons.add(
    sum(octane[o]*x[o, 2] for o in model.oil) >= min_or_extra*sum(x[o, 2] for o in model.oil)
    )

model.demand_cons = pyo.ConstraintList()

model.demand_cons.add(min_dem_reg <= sum(x[o, 1] for o in model.oil))
model.demand_cons.add(sum(x[o, 1] for o in model.oil) <= max_dem_reg)

model.demand_cons.add(min_dem_extra <= sum(x[o, 2] for o in model.oil))
model.demand_cons.add(sum(x[o, 2] for o in model.oil) <= max_dem_extra)

model.inventory_cons = pyo.ConstraintList()

model.inventory_cons.add(sum(x[1, g] for g in model.gasoline) <= inv_national)
model.inventory_cons.add(sum(x[2, g] for g in model.gasoline) <= inv_imported)

# Objective Function

def obj_fn(model):
    return (selling_price_reg*sum(x[o, 1] for o in model.oil) 
            + selling_price_extra*sum(x[o, 2] for o in model.oil))
model.obj = pyo.Objective(rule = obj_fn, sense = pyo.maximize)

# Solution

sol = SolverFactory("cplex")
res = sol.solve(model)

# Printing the Results

for o in model.oil:
    for g in model.gasoline:
        print(f"Barrels of {oils[o]}-Oil used for producing {gasolines[g]}-Gasoline : {x[o, g]()}")

print(f"Total profit obtained from selling the barrels : {model.obj()} $.")

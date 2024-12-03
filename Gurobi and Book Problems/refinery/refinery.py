import pyomo.environ as pyo, gurobipy as gp, numpy as np
from pyomo.opt import SolverFactory

# Parameters

crude_numbers = [1, 2]
petrols = ["Premium_fuel", "Regular_fuel"]
end_produce_names = ["Premium_fuel", "Regular_fuel", "Jet_fuel", "Fuel_oil", "Lube_oil"]
distillation_products_names = ["Light_naphtha", "Medium_naphtha", "Heavy_naphtha",
                               "Light_oil", "Heavy_oil", "Residuum"]
naphthas = ["Light_naphtha", "Medium_naphtha", "Heavy_naphtha"]
intermediate_oils = ["Light_oil", "Heavy_oil"]
cracking_products_names = ["Cracked_gasoline", "Cracked_oil"]
used_for_motor_fuel_names = ["Light_naphtha", "Medium_naphtha", "Heavy_naphtha",
                             "Reformed_gasoline", "Cracked_gasoline"]
used_for_jet_fuel_names = ["Light_oil", "Heavy_oil", "Residuum", "Cracked_oil"]

buy_limit = {1:20000, 2:30000}
lbo_min = 500
lbo_max = 1000

distill_cap = 45000
reform_cap = 10000
crack_cap = 8000

distillation_splitting_coefficients = {"Light_naphtha": (0.1, 0.15),
                          "Medium_naphtha": (0.2, 0.25),
                         "Heavy_naphtha": (0.2, 0.18),
                         "Light_oil": (0.12, 0.08),
                         "Heavy_oil": (0.2, 0.19),
                         "Residuum": (0.13, 0.12)}

cracking_splitting_coefficients = {("Light_oil","Cracked_oil"): 0.68,
                                   ("Heavy_oil","Cracked_oil"): 0.75,
                                   ("Light_oil","Cracked_gasoline"): 0.28,
                                   ("Heavy_oil","Cracked_gasoline"): 0.2}

reforming_splitting_coefficients = {"Light_naphtha": 0.6, "Medium_naphtha":0.52, "Heavy_naphtha":0.45}

end_product_profit = {"Premium_fuel":7, "Regular_fuel":6, "Jet_fuel":4, "Fuel_oil":3.5, "Lube_oil":1.5}

blending_coefficients = {"Light_oil": 0.55, "Heavy_oil": 0.17, "Cracked_oil": 0.22, "Residuum": 0.055}

lube_oil_factor = 0.5
pmf_rmf_ratio = 0.4

octane_number_coefficients = {
    "Light_naphtha":90,
    "Medium_naphtha":80,
    "Heavy_naphtha":70,
    "Reformed_gasoline":115,
    "Cracked_gasoline":105,
}

octane_number_fuel = {"Premium_fuel": 94,"Regular_fuel": 84}

vapour_pressure_constants = [0.6, 1.5, 0.05]

# Model

model = pyo.ConcreteModel()

# Variables

def crudes_ub(model, cn):
    return (0, buy_limit[cn])

model.crudes = pyo.Var(crude_numbers, within = pyo.NonNegativeReals, 
                       bounds = crudes_ub)
crudes = model.crudes

model.end_products = pyo.Var(end_produce_names, within = pyo.NonNegativeReals)
end_products = model.end_products

model.distillation_products = pyo.Var(distillation_products_names, 
                                within = pyo.NonNegativeReals)
distillation_products = model.distillation_products

model.reform_usage = pyo.Var(naphthas, within = pyo.NonNegativeReals)
reform_usage = model.reform_usage

model.reformed_gasoline = pyo.Var(within = pyo.NonNegativeReals)
reformed_gasoline = model.reformed_gasoline

model.cracking_usage = pyo.Var(intermediate_oils, within = pyo.NonNegativeReals)
cracking_usage = model.cracking_usage

model.cracking_products = pyo.Var(cracking_products_names, within = pyo.NonNegativeReals)
cracking_products = model.cracking_products

model.used_for_regular_motor_fuel = pyo.Var(used_for_motor_fuel_names, 
                                      within = pyo.NonNegativeReals)
used_for_regular_motor_fuel = model.used_for_regular_motor_fuel

model.used_for_premium_motor_fuel = pyo.Var(used_for_motor_fuel_names, 
                                      within = pyo.NonNegativeReals)
used_for_premium_motor_fuel = model.used_for_premium_motor_fuel

model.used_for_jet_fuel = pyo.Var(used_for_jet_fuel_names, 
                                  within = pyo.NonNegativeReals)
used_for_jet_fuel = model.used_for_jet_fuel

model.used_for_lube_oil = pyo.Var(within = pyo.NonNegativeReals)
used_for_lube_oil = model.used_for_lube_oil

# Constraints

"""First taking care of bounds"""
model.end_products_lube_oil = pyo.ConstraintList()

model.end_products_lube_oil.add((lbo_min, end_products["Lube_oil"], lbo_max))

expr_1 = pyo.quicksum(crudes[c] for c in crude_numbers) <= distill_cap
model.distillation_cap = pyo.Constraint(expr = expr_1)

expr_2 = pyo.quicksum(reform_usage[nap] for nap in naphthas) <= reform_cap
model.reforming_cap = pyo.Constraint(expr = expr_2)

expr_3 = (pyo.quicksum(cracking_usage[oil] for oil in intermediate_oils) 
          <= crack_cap)
model.cracking_cap = pyo.Constraint(expr = expr_3)

def yield_crude_oil(model, dpn):
    return pyo.quicksum(distillation_splitting_coefficients[dpn][crude-1]*crudes[crude] 
                        for crude in crudes) == distillation_products[dpn]
model.c4 = pyo.Constraint(distillation_products_names, rule = yield_crude_oil)

expr_5 = (pyo.quicksum(reforming_splitting_coefficients[nap]*reform_usage[nap] 
                       for nap in reform_usage) == reformed_gasoline)
model.yield_naphthas = pyo.Constraint(expr = expr_5)

def yield_cracking_oil(model, crack_prod):
    return (pyo.quicksum(cracking_splitting_coefficients[oil, crack_prod]
                        *cracking_usage[oil] 
                        for oil in intermediate_oils) 
            == cracking_products[crack_prod])
model.c6 = pyo.Constraint(cracking_products_names, rule = yield_cracking_oil)

expr_7 = lube_oil_factor*used_for_lube_oil == end_products["Lube_oil"]
model.c7 = pyo.Constraint(expr = expr_7)

# Blending Premium Fuel
expr_8 = (pyo.quicksum(used_for_premium_motor_fuel[fuel] 
                       for fuel in used_for_motor_fuel_names) 
          == end_products["Premium_fuel"])
model.yield_premium = pyo.Constraint(expr = expr_8)

# Blending Premium Fuel
expr_9 = (pyo.quicksum(used_for_regular_motor_fuel[fuel] 
                       for fuel in used_for_motor_fuel_names) 
          == end_products["Regular_fuel"])
model.yield_regular = pyo.Constraint(expr = expr_9)

# Continuity Jet Fuel
expr_10 = (pyo.quicksum(used_for_jet_fuel[fuel] 
                        for fuel in used_for_jet_fuel_names) 
           == end_products["Jet_fuel"])
model.continuity_jet_fuel = pyo.Constraint(expr = expr_10)

# Now below are the constraints of Mass Conservation

def naphtha_mass_conservation(model, nap):
    return (reform_usage[nap] 
            + used_for_regular_motor_fuel[nap] 
            + used_for_premium_motor_fuel[nap] 
            == distillation_products[nap])
model.c11 = pyo.Constraint(naphthas, rule = naphtha_mass_conservation)

def light_oil_mass_conservation(model):
    return (cracking_usage["Light_oil"] 
            + used_for_jet_fuel["Light_oil"] 
            + blending_coefficients["Light_oil"]*end_products["Fuel_oil"] 
            == distillation_products["Light_oil"])
model.c12 = pyo.Constraint(rule = light_oil_mass_conservation)

def heavy_oil_mass_conservation(model):
    return (cracking_usage["Heavy_oil"] 
            + used_for_jet_fuel["Heavy_oil"] 
            + blending_coefficients["Heavy_oil"]*end_products["Fuel_oil"] 
            == distillation_products["Heavy_oil"])
model.c13 = pyo.Constraint(rule = heavy_oil_mass_conservation)

def cracked_oil_mass_conservation(model):
    return (used_for_jet_fuel["Cracked_oil"] 
            + blending_coefficients["Cracked_oil"]*end_products["Fuel_oil"] 
            == cracking_products["Cracked_oil"])
model.c14 = pyo.Constraint(rule = cracked_oil_mass_conservation)

def residuum_mass_conservation(model):
    return (used_for_lube_oil 
            + used_for_jet_fuel["Residuum"] 
            + blending_coefficients["Residuum"]*end_products["Fuel_oil"] 
            == distillation_products["Residuum"])
model.c15 = pyo.Constraint(rule = residuum_mass_conservation)

def cracked_gasoline_mass_conservation(model):
    return (used_for_regular_motor_fuel["Cracked_gasoline"] 
            + used_for_premium_motor_fuel["Cracked_gasoline"] 
            == cracking_products["Cracked_gasoline"])
model.c16 = pyo.Constraint(rule = cracked_gasoline_mass_conservation)

def reformed_gasoline_mass_conservation(model):
    return (used_for_regular_motor_fuel["Reformed_gasoline"] 
            + used_for_premium_motor_fuel["Reformed_gasoline"] 
            == reformed_gasoline)
model.c17 = pyo.Constraint(rule = reformed_gasoline_mass_conservation)

# Premium to Regular Proportion

def premium_to_regular_proportion(model):
    return (end_products["Premium_fuel"] >= pmf_rmf_ratio*end_products["Regular_fuel"])
model.c18 = pyo.Constraint(rule = premium_to_regular_proportion)

# Octane Tolerance

def octane_regular(model):
    return (pyo.quicksum(used_for_regular_motor_fuel[fuel]*octane_number_coefficients[fuel] 
                         for fuel in used_for_motor_fuel_names) 
            >= octane_number_fuel["Regular_fuel"]*end_products["Regular_fuel"])
model.c19 = pyo.Constraint(rule = octane_regular)

def octane_premium(model):
    return (pyo.quicksum(used_for_premium_motor_fuel[fuel]*octane_number_coefficients[fuel] 
                         for fuel in used_for_motor_fuel_names) 
            >= octane_number_fuel["Premium_fuel"]*end_products["Premium_fuel"])
model.c20 = pyo.Constraint(rule = octane_premium)

# Vapour Pressure Tolerance

def vap_pressure_tol(model):
    return (used_for_jet_fuel["Light_oil"] 
            + vapour_pressure_constants[0]*used_for_jet_fuel["Heavy_oil"] 
            + vapour_pressure_constants[1]*used_for_jet_fuel["Cracked_oil"] 
            + vapour_pressure_constants[2]*used_for_jet_fuel["Residuum"] 
            <= end_products["Jet_fuel"])
model.c21 = pyo.Constraint(rule = vap_pressure_tol)

# Objective Function

def obj_fn(model):
    return pyo.quicksum(end_products[prod]*end_product_profit[prod] 
                        for prod in end_produce_names)
model.obj = pyo.Objective(rule = obj_fn, sense = pyo.maximize)

# Solution

sol = SolverFactory("cplex")
res = sol.solve(model)

# Printing the Solution

print(res)








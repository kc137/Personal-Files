import pyomo.environ as pyo, pandas as pd, numpy as np
from pyomo.opt import SolverFactory

NM = 5
NP = 7
months = 6
inventory_june = 50
max_holding_capacity = 100
holding_cost = 0.5

machine_to_no_dict = {1 : "Grinding", 
                      2 : "Vertical Drilling", 
                      3 : "Horizontal Drilling", 
                      4 : "Boring", 
                      5 : "Planning"}

df_1 = pd.read_excel("factory_planning_1.xlsx", sheet_name = "Time and Profit", 
                     index_col = 0)
df_2 = pd.read_excel("factory_planning_1.xlsx", sheet_name = "Downtime", 
                     index_col = 0)

# df_1.infer_objects(copy = False).replace("-", 0)
df_1 = df_1.astype(str).replace("-", 0)
df_1 = df_1.astype(float)

df_1.index = list(range(0, NM+1))
df_1.columns = list(range(1, NP+1))
# print(type(df_1.iloc[0, 3]))

df_2 = df_2.rename({"January" : 1, 
                    "February" : 2,
                    "March" : 3, 
                    "April" : 4, 
                    "May" : 5, 
                    "June" : 6}
                   )
# print(df_1)
# print(df_2)

profits = list(df_1.iloc[0, :])

product_limitations = []
with open("total_products_limitations.txt", "r") as products_data:
    lines = products_data.read().splitlines()
    for line in lines[1:]:
        products_str = line.split()
        product_limitations.append([int(hour) for hour in products_str[1:]])

installed_machines = [4, 2, 3, 1, 1]

# Model

model = pyo.ConcreteModel()

# Sets and Parameters

model.m = pyo.RangeSet(1, 5)
model.p = pyo.RangeSet(1, 7)
model.t = pyo.RangeSet(1, 6)

# Variables

model.x = pyo.Var(model.t, model.p, within = pyo.NonNegativeReals)
x = model.x

model.ph = pyo.Var(model.t, model.p, within = pyo.NonNegativeReals)
ph = model.ph

model.ps = pyo.Var(model.t, model.p, within = pyo.NonNegativeReals)
ps = model.ps

# Constraints

def initial_month_product(model, p):
    return x[1, p] == ps[1, p] + ph[1, p]
model.c1 = pyo.Constraint(model.p, rule = initial_month_product)

def other_months_product(model, t, p):
    if t == 1:
        return pyo.Constraint.Skip
    else:
        return ph[t-1, p] + x[t, p] == ps[t, p] + ph[t, p]
model.c2 = pyo.Constraint(model.t, model.p, rule = other_months_product)

def inventory_target(model, p):
    return ph[6, p] == inventory_june
model.c3 = pyo.Constraint(model.p, rule = inventory_target)

def max_products(model, t, p):
    return ps[t, p] <= product_limitations[t-1][p-1]
model.c4 = pyo.Constraint(model.t, model.p, rule = max_products)

def max_inventory(model, t, p):
    return ph[t, p] <= max_holding_capacity
model.c5 = pyo.Constraint(model.t, model.p, rule = max_inventory)

def machine_capacity(model, t, m):
    return pyo.quicksum(df_1.iloc[m, p-1]*x[t, p] for p in model.p) <= \
           (24*2*8)*(installed_machines[m-1] - df_2.iloc[t-1, m-1])
model.c6 = pyo.Constraint(model.t, model.m, rule = machine_capacity)

# Objective Function

def obj_fn(model):
    return pyo.quicksum(profits[p-1]*x[t, p] - holding_cost*ph[t, p] 
                        for t in model.t 
                        for p in model.p)
model.obj = pyo.Objective(rule = obj_fn, sense = pyo.maximize)

# Solution

sol = SolverFactory("cplex")
res = sol.solve(model)

# Printing the Solution

print(f"The total Profit for the Cornish Engineering Company : {model.obj()} $.")

# output = np.zeros(shape = [months, NP], dtype = float)
output = [[0 for _ in range(NP)] for _ in range(months)]

for t in model.t:
    for p in model.p:
        output[t-1][p-1] = ps[t, p]()
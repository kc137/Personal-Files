import pyomo.environ as pyo, gurobipy as gp, pandas as pd, numpy as np
from pyomo.opt import SolverFactory

model = pyo.ConcreteModel()

model.years = pyo.RangeSet(1, 5)
years = model.years

model.lands = pyo.RangeSet(1, 4)
lands = model.lands

model.ages = pyo.RangeSet(1, 12)
ages = model.ages

model.cow_ages = pyo.RangeSet(2, 11)
cow_ages = model.cow_ages

gr_area = {1: 20.0, 2: 30.0, 3: 20.0, 4: 10.0} # Groupwise Area
gr_yield = {1: 1.1,  2: 0.9, 3: 0.8, 4:0.65} # Grain Production
sb_yield = 1.5 # Sugar Beet Yield
housing_cap = 130 # Max Cows that can be housed
gr_intake = 0.6 # Per year grains req by a cow
sb_intake = 0.7 # Per year sugar beet req by a cow
hf_land = 2/3 # Acres req for sustaining each Heifer
land_cap = 200 # Land Available
hf_labour = 10/100 # Hours of labour req for sustaining each Heifer
cow_labour = 42/100 # Hours of labour req for sustaining each Cow
gr_labour = 4/100 # Hours of labour req for each acre of land devoted to grains per year
sb_labour = 14/100 # Hours of labour req for rach acre of lane devoted to sugar beet per year
labour_cap = 5500/100 # Regular labour available (hrs) in  year
cow_decay = 0.02 # Avg cows that die in a your
hf_decay = 0.05 # Avg heifers that die in a your
initial_hf = 9.5 # No. of Heifers of each age at the beginning of Planning Horizon
initial_cows = 9.8 # No. of cows of each age at the beginning of Planning Horizon
birthrate = 1.1 # Expected No. of calves produced by a dairy cow each year
min_final_cows = 50 # Min. No. of Dairy Cows at the end of Planning Horizon
max_final_cows = 175 # Max. No. of Dairy Cows at the end of Planning Horizon
bl_price = 30 # Price for selling one Bullock
hf_price = 40 # Price fir selling one Heifer
cow_price = 120 # SP of one Dairy Cow
milk_price = 370 # SP of milk produced by a dairy Cow in a year
gr_price = 75 # Price for selling a ton of Grain
sb_price = 58 # Price for selling a ton of Sugar Beet
gr_cost = 90 # CP for a ton of Grain
sb_cost = 70 # CP for a ton of Sugar Beet
overtime_cost = 120 # Cost for getting an hour of overtime
regular_time_cost = 4000 # Cost for 5500 hours of labour in regular time
hf_cost = 50 # Yearly cost for supporting a Heifer
cow_cost = 100 # Yearly cost for supporting a dairy cow
gr_land_cost = 15 # Yearly cost for supporting an acre of land devoted to grain
sb_land_cost = 10 # Yearly cost for supporting an acre of land devoted to sugar beet
installment = 39.71 # Annual payment for each $200 of loan (39.71 is given and calculated value is 39.85)

# Variables

# Tons of SB to grow in a year
model.sb = pyo.Var(years, within = pyo.NonNegativeReals)
sb = model.sb

# Tons of grains to buy in a year
model.gr_buy = pyo.Var(years, within = pyo.NonNegativeReals)
gr_buy = model.gr_buy

# Tons of grains to sell in a year
model.gr_sell = pyo.Var(years, within = pyo.NonNegativeReals)
gr_sell = model.gr_sell

# Tons of SB to buy in a year
model.sb_buy = pyo.Var(years, within = pyo.NonNegativeReals)
sb_buy = model.sb_buy

# Tons of SB to sell in a year
model.sb_sell = pyo.Var(years, within = pyo.NonNegativeReals)
sb_sell = model.sb_sell

# No of extra labour hours needed in a year
model.overtime = pyo.Var(years, within = pyo.NonNegativeReals)
overtime = model.overtime

# Amount of money (in $200) spent on renting in a year (Capital Outlay)
model.outlay = pyo.Var(years, within = pyo.NonNegativeReals)
outlay = model.outlay

# No. of newborn Heifers to sell in a year
model.hf_sell = pyo.Var(years, within = pyo.NonNegativeReals)
hf_sell = model.hf_sell

# No. of newborn Heifers left in a year to be raised
model.newborn = pyo.Var(years, within = pyo.NonNegativeReals)
newborn = model.newborn

# Profit attained in a year
model.profit = pyo.Var(years, within = pyo.NonNegativeReals)
profit = model.profit

# Tons of grain grown in a year at a particular land group
model.gr = pyo.Var(years, lands, within = pyo.NonNegativeReals)
gr = model.gr

# No. of cows at age k available in year t
model.cows = pyo.Var(years, ages, within = pyo.NonNegativeReals)
cows = model.cows

# Constraints

# Housing Capacity

def housing_cap_cons(model, t):
    return (newborn[t] + 
            pyo.quicksum(cows[t, k] for k in ages if k != 12) <= 
            housing_cap + 
            pyo.quicksum(outlay[d] for d in years if d <= t))
model.c1 = pyo.Constraint(years, rule = housing_cap_cons)

# Food Consumption (Grains)

def fc_grain(model, t):
    return (pyo.quicksum(gr_intake*cows[t, k] for k in cow_ages) <= 
            gr_buy[t] - gr_sell[t] + 
            pyo.quicksum(gr[t, l] for l in lands))
model.c2 = pyo.Constraint(years, rule = fc_grain)

# Food Consumption (Sugar Beet)

def fc_sugar_beet(model, t):
    return (pyo.quicksum(sb_intake*cows[t, k] for k in cow_ages) <= 
            sb_buy[t] - sb_sell[t] + sb[t])
model.c3 = pyo.Constraint(years, rule = fc_sugar_beet)

# Grain Growing

def grain_growing(model, t, l):
    return gr[t, l] <= gr_yield[l]*gr_area[l]
model.c4 = pyo.Constraint(years, lands, rule = grain_growing)

# Land Capacity

def land_capacity(model, t):
    return ((sb[t]/sb_yield) + hf_land*(newborn[t] + cows[t, 1]) + 
            pyo.quicksum(cows[t, k] for k in cow_ages) + 
            pyo.quicksum((gr[t, l]/gr_yield[l]) for l in lands) <= 
            land_cap)
model.c5 = pyo.Constraint(years, rule = land_capacity)

# Labour

def labour(model, t):
    return (hf_labour*(newborn[t] + cows[t, 1]) + 
           pyo.quicksum(cow_labour*cows[t, k] for k in cow_ages) + 
           pyo.quicksum((gr_labour/gr_yield[l])*gr[t, l] for l in lands) + 
           (sb_labour/sb_yield)*sb[t] <= 
           labour_cap + overtime[t])
model.c6 = pyo.Constraint(years, rule = labour)

# Continuity - Livestock in year(t) have to survive previous year

def continuity_1(model, t):
    if t != 1:
        return cows[t, 1] == (1 - hf_decay)*newborn[t-1]
    else:
        return pyo.Constraint.Skip
model.c7 = pyo.Constraint(years, rule = continuity_1)

def continuity_2(model, t):
    if t != 1:
        return cows[t, 2] == (1 - hf_decay)*cows[t-1, 1]
    else:
        return pyo.Constraint.Skip
model.c8 = pyo.Constraint(years, rule = continuity_2)

def continuity_3(model, t, k):
    if t != 1:
        return cows[t, k+1] == (1 - cow_decay)*cows[t-1, k]
    else:
        return pyo.Constraint.Skip
model.c9 = pyo.Constraint(years, cow_ages, rule = continuity_3)

# Heifers born in year(t) depend on the no. of dairy cows

def heifers_birth(model, t):
    return newborn[t] + hf_sell[t] == pyo.quicksum((birthrate/2)*cows[t, k] 
                                                   for k in cow_ages)
model.c10 = pyo.Constraint(years, rule = heifers_birth)

# Final Dairy Cows - At the end of the planning horizon

def final_cows(model):
    return (min_final_cows, 
            pyo.quicksum(cows[5, k] for k in cow_ages), 
            max_final_cows)
model.c11 = pyo.Constraint(rule = final_cows)

"""
Initial Conditions - Set the number of livestock available 
at the beginning of planning horizon
"""

model.initial_conditions = pyo.ConstraintList()

for k in ages:
    if k <= 2:
        model.initial_conditions.add(cows[1, k] == initial_hf)
    else:
        model.initial_conditions.add(cows[1, k] == initial_cows)

"""
Yearly Profit - Profit in year(t) driven by operations from crops and livestock, 
after accounting for labour, land and financial costs
"""

def profit_equality(model, t):
    return (profit[t] == 
            ((bl_price*birthrate)/2)*pyo.quicksum(cows[t, k] for k in cow_ages) + 
            hf_price*hf_sell[t] + cow_price*cows[t, 12] + 
            milk_price*pyo.quicksum(cows[t, k] for k in cow_ages) + 
            gr_price*gr_sell[t] + sb_price*sb_sell[t] - 
            gr_cost*gr_buy[t] - sb_cost*sb_buy[t] - 
            overtime_cost*overtime[t] - regular_time_cost - 
            hf_cost*(newborn[t] + cows[t, 1]) - 
            cow_cost*pyo.quicksum(cows[t, k] for k in cow_ages) - 
            gr_land_cost*pyo.quicksum((gr[t, l]/gr_yield[l]) for l in lands) - 
            sb_land_cost*(sb[t]/sb_yield) - 
            installment*pyo.quicksum(outlay[d] for d in years if d <= t))
model.c13 = pyo.Constraint(years, rule = profit_equality)

# Objective Function

def obj_fn(model):
    return (pyo.quicksum(profit[t] - 
            installment*(t+4)*outlay[t] 
            for t in years))
model.obj = pyo.Objective(rule = obj_fn, sense = pyo.maximize)

# Solution

sol = SolverFactory("cplex")
res = sol.solve(model)

# Printing the Solution

max_profit = round(model.obj(), 3)
print(f"The profit over the five-year period : ${max_profit}")
# print(res)


import numpy as np
import pandas as pd

import gurobipy as gp
from gurobipy import GRB

# tested with Python 3.7.0 & Gurobi 9.0

# Parameters

years = [1,2,3,4,5]
lands = [1,2,3,4]
ages = [1,2,3,4,5,6,7,8,9,10,11,12]
cow_ages = [2,3,4,5,6,7,8,9,10,11]

gr_area = {1: 20.0, 2: 30.0, 3: 20.0, 4: 10.0}
gr_yield = {1: 1.1,  2: 0.9, 3: 0.8, 4:0.65}
sb_yield = 1.5
housing_cap = 130
gr_intake = 0.6
sb_intake = 0.7
hf_land = 2/3.0
land_cap = 200
hf_labor = 10/100.0
cow_labor = 42/100.0
gr_labor = 4/100.0
sb_labor = 14/100.0
labor_cap = 5500/100.0
cow_decay = 0.02
hf_decay = 0.05
initial_hf = 9.5
initial_cows = 9.8
birthrate = 1.1
min_final_cows = 50
max_final_cows = 175
bl_price = 30
hf_price = 40
cow_price = 120
milk_price = 370
gr_price = 75
sb_price = 58
gr_cost = 90
sb_cost = 70
overtime_cost = 120
regular_time_cost = 4000
hf_cost = 50
cow_cost = 100
gr_land_cost = 15
sb_land_cost = 10
installment = 39.71

model = gp.Model('Farming')
sb = model.addVars(years, vtype=GRB.CONTINUOUS, name="SB")
gr_buy = model.addVars(years, vtype=GRB.CONTINUOUS, name="GR_buy")
gr_sell = model.addVars(years, vtype=GRB.CONTINUOUS, name="GR_sell")
sb_buy = model.addVars(years, vtype=GRB.CONTINUOUS, name="SB_buy")
sb_sell = model.addVars(years, vtype=GRB.CONTINUOUS, name="SB_sell")
overtime = model.addVars(years, vtype=GRB.CONTINUOUS, name="Overtime")
outlay = model.addVars(years, vtype=GRB.CONTINUOUS, name="Outlay")
hf_sell = model.addVars(years, vtype=GRB.CONTINUOUS, name="HF_sell")
newborn = model.addVars(years, vtype=GRB.CONTINUOUS, name="Newborn")
profit = model.addVars(years, vtype=GRB.CONTINUOUS, name="Profit")
gr = model.addVars(years, lands, vtype=GRB.CONTINUOUS, name="GR")
cows = model.addVars(years, ages, vtype=GRB.CONTINUOUS, name="Cows")

# 1. Housing capacity

HousingCap = model.addConstrs((newborn[year] +
                    cows[year,1] +
                    gp.quicksum(cows[year,age] for age in cow_ages) -
                    gp.quicksum(outlay[d] for d in years if d <= year)
                    <= housing_cap for year in years), name="Housing_cap")

# 2.1 Food consumption (Grain)

GrainConsumption = model.addConstrs((gp.quicksum(gr_intake*cows[year, age] for age in cow_ages)
                  <= gr_buy[year] - gr_sell[year] + gr.sum(year, '*')
                  for year in years), name="Grain_consumption")

# 2.1 Food consumption (Sugar beet)
SugarbeetConsumption = model.addConstrs((gp.quicksum(sb_intake*cows[year, age] for age in cow_ages)
                  <= sb_buy[year] - sb_sell[year] + sb[year]
                  for year in years), name="Sugar_beet_consumption")

# 3. Grain growing

GrainGrowing = model.addConstrs((gr[year, land] <= gr_yield[land]*gr_area[land]
                  for year in years for land in lands), name="Grain_growing")

# 4. Land capacity

LandCap = model.addConstrs((sb[year]/sb_yield + hf_land*(newborn[year] + cows[year,1])
                  + gp.quicksum((1/gr_yield[land])*gr[year, land] for land in lands)
                  + gp.quicksum(cows[year, age] for age in cow_ages)
                  <= land_cap for year in years), name="Land_capacity")

# 5. Labor

Labor = model.addConstrs((hf_labor*(newborn[year] + cows[year,1])
                  + gp.quicksum(cow_labor*cows[year, age] for age in cow_ages)
                  + gp.quicksum(gr_labor/gr_yield[land]*gr[year,land] for land in lands)
                  + sb_labor/sb_yield*sb[year] 
                  <= labor_cap + overtime[year] for year in years), name="Labor")

# 6.1 Continuity

Continuity1 = model.addConstrs((cows[year,1] == (1-hf_decay)*newborn[year-1] 
                  for year in years if year > min(years)),
                 name="Continuity_a")

# 6.2 Continuity

Continuity2 = model.addConstrs((cows[year,2] == (1-hf_decay)*cows[year-1,1] 
                  for year in years if year > min(years)),
                 name="Continuity_b")

# 6.3 Continuity

Continuity3 = model.addConstrs((cows[year,age+1] == (1-cow_decay)*cows[year-1,age] 
                  for year in years for age in cow_ages if year > min(years)),
                 name="Continuity_c")

# 7. Heifers birth

HeifersBirth = model.addConstrs((newborn[year] + hf_sell[year] 
                  == gp.quicksum(birthrate/2*cows[year,age] for age in cow_ages) for year in years)
                 , name="Heifers_birth")

# 8. Final dairy cows
FinalDairyCows = model.addRange(gp.quicksum(cows[max(years), age] for age in cow_ages), min_final_cows, max_final_cows, name="Final_dairy_cows" )

# 9.1-9.2 Initial conditions

InitialHeifers = model.addConstrs((initial_hf == cows[1, age] for age in ages if age < 3),
                 name="Initial_conditions")

# 9.3 Initial conditions

InitialCows = model.addConstrs((initial_cows == cows[1, age] for age in ages if age >= 3),
                 name="Initial_condition_cows")

# 10. Yearly profit

YearlyProfit = model.addConstrs((profit[year]
                  == bl_price*birthrate/2*gp.quicksum(cows[year, age] for age in cow_ages)
                  + hf_price*hf_sell[year] + cow_price*cows[year, 12]
                  + milk_price*gp.quicksum(cows[year, age] for age in cow_ages)
                  + gr_price*gr_sell[year] + sb_price*sb_sell[year]
                  - gr_cost*gr_buy[year] - sb_cost*sb_buy[year]
                  - overtime_cost*overtime[year] - regular_time_cost
                  - hf_cost*(newborn[year] + cows[year,1])
                  - cow_cost*gp.quicksum(cows[year, age] for age in cow_ages)
                  - gr_land_cost*gp.quicksum(gr[year, land]/gr_yield[land] for land in lands)
                  - sb_land_cost*sb[year]/sb_yield
                  - installment*gp.quicksum(outlay[d] for d in years if d <= year)
                  for year in years), name="Yearly_profit")

# 0. Total profit

model.setObjective(gp.quicksum(profit[year] - installment*(year+4)*outlay[year] for year in years), GRB.MAXIMIZE)

model.optimize()


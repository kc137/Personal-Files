import pyomo.environ as pyo, gurobipy as gp, numpy as np, pandas as pd
from pyomo.opt import SolverFactory

# Create a dictionary to capture the delivery points and spirit market -in millions of gallons.

retailers, deliveryPoints, spiritMarket = gp.multidict({
    1: [11,34],
    2: [47,411],
    3: [44,82],
    4: [25,157],
    5: [10,5],
    6: [26,183],
    7: [26,14],
    8: [54,215],
    9: [18,102],
    10: [51,21],
    11: [20,54],
    12: [105,0],
    13: [7,6],
    14: [16,96],
    15: [34,118],
    16: [100,112],
    17: [50,535],
    18: [21,8],
    19: [11,53],
    20: [19,28],
    21: [14,69],
    22: [10,65],
    23: [11,27]
})

# Create a dictionary to capture the oil market -in millions of gallons for region 1.

retailers1,  oilMarket1 = gp.multidict({
    (1): 9,
    (2): 13,
    (3): 14,
    (4): 17,
    (5): 18,
    (6): 19,
    (7): 23,
    (8): 21
})

# Create a dictionary to capture the oil market -in millions of gallons for region 2.

retailers2,  oilMarket2 = gp.multidict({
    (9): 9,
    (10): 11,
    (11): 17,
    (12): 18,
    (13): 18,
    (14): 17,
    (15): 22,
    (16): 24,
    (17): 36,
    (18): 43
})

# Create a dictionary to capture the oil market -in millions of gallons for region 3.

retailers3,  oilMarket3 = gp.multidict({
    (19): 6,
    (20): 15,
    (21): 15,
    (22): 25,
    (23): 39
})

# Create a dictionary to capture retailers in group A.

groupA,  retailerA = gp.multidict({
    (1): 1,
    (2): 1,
    (3): 1,
    (5): 1,
    (6): 1,
    (10): 1,
    (15): 1,
    (20): 1
})

# Create a dictionary to capture retailers in group B.

groupB,  retailerB = gp.multidict({
    (4): 1,
    (7): 1,
    (8): 1,
    (9): 1,
    (11): 1,
    (12): 1,
    (13): 1,
    (14): 1,
    (16): 1,
    (17): 1,
    (18): 1,
    (19): 1,
    (21): 1,
    (22): 1,
    (23): 1
})

# Forty and five percentages of each goal

deliveryPoints40 = 292
deliveryPoints5 = 36.5
spiritMarket40 = 958
spiritMarket5 = 119.75
oilMarket1_40 = 53.6
oilMarket1_5 = 6.7
oilMarket2_40 = 86
oilMarket2_5 = 10.75
oilMarket3_40 = 40
oilMarket3_5 = 5
retailerA40 = 3.2
retailerA5 = 0.4
retailerB40 = 6
retailerB5 = 0.75

# Model

model = pyo.ConcreteModel()

# Allocate retailers to Division 1.

model.allocate = pyo.Var(retailers, within = pyo.Binary)
allocate = model.allocate

# Deviations of delivery points goal

model.deliveryPointsPos = pyo.Var(within = pyo.NonNegativeReals, bounds = (0, deliveryPoints5))
deliveryPointsPos = model.deliveryPointsPos

model.deliveryPointsNeg = pyo.Var(within = pyo.NonNegativeReals, bounds = (0, deliveryPoints5))
deliveryPointsNeg = model.deliveryPointsNeg

# Deviations of spirit market goal

model.spiritMarketPos = pyo.Var(within = pyo.NonNegativeReals, bounds = (0, spiritMarket5))
spiritMarketPos = model.spiritMarketPos

model.spiritMarketNeg = pyo.Var(within = pyo.NonNegativeReals, bounds = (0, spiritMarket5))
spiritMarketNeg = model.spiritMarketNeg

# Deviatons of oil market in region 1 goal

model.oilMarket1Pos = pyo.Var(within = pyo.NonNegativeReals, bounds = (0, oilMarket1_5))
oilMarket1Pos = model.oilMarket1Pos

model.oilMarket1Neg = pyo.Var(within = pyo.NonNegativeReals, bounds = (0, oilMarket1_5))
oilMarket1Neg = model.oilMarket1Neg

# Deviatons of oil market in region 2 goal

model.oilMarket2Pos = pyo.Var(within = pyo.NonNegativeReals, bounds = (0, oilMarket2_5))
oilMarket2Pos = model.oilMarket2Pos

model.oilMarket2Neg = pyo.Var(within = pyo.NonNegativeReals, bounds = (0, oilMarket2_5))
oilMarket2Neg = model.oilMarket2Neg

# Deviatons of oil market in region 3 goal

model.oilMarket3Pos = pyo.Var(within = pyo.NonNegativeReals, bounds = (0, oilMarket3_5))
oilMarket3Pos = model.oilMarket3Pos

model.oilMarket3Neg = pyo.Var(within = pyo.NonNegativeReals, bounds = (0, oilMarket3_5))
oilMarket3Neg = model.oilMarket3Neg

# Deviations of retailers in group-A goal

model.retailerAPos = pyo.Var(within = pyo.NonNegativeReals, bounds = (0, retailerA5))
retailerAPos = model.retailerAPos

model.retailerANeg = pyo.Var(within = pyo.NonNegativeReals, bounds = (0, retailerA5))
retailerANeg = model.retailerANeg

# Deviations of retailers in group-B goal

model.retailerBPos = pyo.Var(within = pyo.NonNegativeReals, bounds = (0, retailerB5))
retailerBPos = model.retailerBPos

model.retailerBNeg= pyo.Var(within = pyo.NonNegativeReals, bounds = (0, retailerB5))
retailerBNeg = model.retailerBNeg

# Constraints

"""
The allocation of retailers at Division 1 satisfies as much as possible 
forty percent of the delivery points.
"""

def delivery_points(model):
    return (pyo.quicksum(deliveryPoints[r]*allocate[r] for r in retailers) 
            + deliveryPointsPos 
            - deliveryPointsNeg 
            == deliveryPoints40)
model.c1 = pyo.Constraint(rule = delivery_points)

"""
The allocation of retailers at Division 1 satisfies as much as possible 
forty percent of the spirit market.
"""

def spirit_market(model):
    return (pyo.quicksum(spiritMarket[r]*allocate[r] 
                         for r in retailers) 
            + spiritMarketPos 
            - spiritMarketNeg 
            == spiritMarket40)
model.c2 = pyo.Constraint(rule = spirit_market)

"""
The allocation of retailers in region 1 at Division 1 satisfies as much as
possible forty percent of the oil market in that region.
"""

def oil_market_reg_1(model):
    return (pyo.quicksum(oilMarket1[r]*allocate[r] 
                         for r in retailers1) 
            + oilMarket1Pos 
            - oilMarket1Neg 
            == oilMarket1_40)
model.c3 = pyo.Constraint(rule = oil_market_reg_1)

"""
The allocation of retailers in region 2 at Division 1 satisfies as much as
possible forty percent of the oil market in that region.
"""

def oil_market_reg_2(model):
    return (pyo.quicksum(oilMarket2[r]*allocate[r] 
                         for r in retailers2) 
            + oilMarket2Pos 
            - oilMarket2Neg 
            == oilMarket2_40)
model.c4 = pyo.Constraint(rule = oil_market_reg_2)

def oil_market_reg_3(model):
    return (pyo.quicksum(oilMarket3[r]*allocate[r] 
                         for r in retailers3) 
            + oilMarket3Pos 
            - oilMarket3Neg 
            == oilMarket3_40)
model.c5 = pyo.Constraint(rule = oil_market_reg_3)

"""
The allocation of retailers at Division 1 satisfies as much as possible 
forty percent of the retailers in group A.
"""

def group_A(model):
    return (pyo.quicksum(retailerA[r]*allocate[r] 
                         for r in groupA) 
            + retailerAPos 
            - retailerANeg 
            == retailerA40)
model.c6 = pyo.Constraint(rule = group_A)

def group_B(model):
    return (pyo.quicksum(retailerB[r]*allocate[r] 
                         for r in groupB) 
            + retailerBPos 
            - retailerBNeg 
            == retailerB40)
model.c7 = pyo.Constraint(rule = group_B)

# Objective Function

def obj_fn(model):
    return (deliveryPointsPos + deliveryPointsNeg + spiritMarketPos + spiritMarketNeg 
            + oilMarket1Pos + oilMarket1Neg + oilMarket2Pos + oilMarket2Neg 
            + oilMarket3Pos + oilMarket3Neg + retailerAPos + retailerANeg 
            + retailerBPos + retailerBNeg)
model.obj = pyo.Objective(rule = obj_fn, sense = pyo.minimize)

# Solution

sol = SolverFactory("cplex")
res = sol.solve(model)

# Printing the Solution

print(res)










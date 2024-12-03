import numpy as np
import pandas as pd
from itertools import product

import gurobipy as gp
from gurobipy import GRB

# tested with Python 3.7.0 & Gurobi 9.0

# Create a dictionary to capture the delivery points and spirit market -in millions of gallons.

retailers, deliveryPoints, spiritMarket = gp.multidict({
    (1): [11,34],
    (2): [47,411],
    (3): [44,82],
    (4): [25,157],
    (5): [10,5],
    (6): [26,183],
    (7): [26,14],
    (8): [54,215],
    (9): [18,102],
    (10): [51,21],
    (11): [20,54],
    (12): [105,0],
    (13): [7,6],
    (14): [16,96],
    (15): [34,118],
    (16): [100,112],
    (17): [50,535],
    (18): [21,8],
    (19): [11,53],
    (20): [19,28],
    (21): [14,69],
    (22): [10,65],
    (23): [11,27]
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

model = gp.Model('MarketSharing')

# Allocation of retailers to Division 1.
allocate = model.addVars(retailers, vtype=GRB.BINARY, name="allocate")

# Positive and negative deviation of delivery points goal.

deliveryPointsPos = model.addVar(ub= deliveryPoints5, name='deliveryPointsPos')
deliveryPointsNeg = model.addVar(ub= deliveryPoints5, name='deliveryPointsNeg')

# Positive and negative deviation of spirit market goal.

spiritMarketPos = model.addVar(ub=spiritMarket5, name='spiritMarketPos')
spiritMarketNeg = model.addVar(ub=spiritMarket5, name='spiritMarketNeg')

# Positive and negative deviation of oil market in region 1 goal.

oilMarket1Pos = model.addVar(ub=oilMarket1_5, name='oilMarket1Pos')
oilMarket1Neg = model.addVar(ub=oilMarket1_5, name='oilMarket1Neg')

# Positive and negative deviation of oil market in region 2 goal.

oilMarket2Pos = model.addVar(ub=oilMarket2_5, name='oilMarket2Pos')
oilMarket2Neg = model.addVar(ub=oilMarket2_5, name='oilMarket2Neg')

# Positive and negative deviation of oil market in region 3 goal.

oilMarket3Pos = model.addVar(ub=oilMarket3_5, name='oilMarket3Pos')
oilMarket3Neg = model.addVar(ub=oilMarket3_5, name='oilMarket3Neg')

# Positive and negative deviation of retailers in group A goal.

retailerAPos  = model.addVar(ub=retailerA5, name='retailerAPos')
retailerANeg  = model.addVar(ub=retailerA5, name='retailerANeg')

# Positive and negative deviation of retailers in group B goal.

retailerBPos  = model.addVar(ub=retailerB5, name='retailerBPos')
retailerBNeg  = model.addVar(ub=retailerB5, name='retailerBNeg')

# Delivery points constraint.

DPConstr = model.addConstr((gp.quicksum(deliveryPoints[r]*allocate[r] for r in retailers) 
                            + deliveryPointsPos - deliveryPointsNeg == deliveryPoints40), name='DPConstrs')
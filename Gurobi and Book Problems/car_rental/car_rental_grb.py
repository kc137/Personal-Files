import pandas as pd
from itertools import product

import gurobipy as gp
from gurobipy import GRB

# tested with Python 3.7.0 & Gurobi 9.0

# list of depots and working days of a week

depots = ['Glasgow','Manchester','Birmingham','Plymouth']
NRD = ['Glasgow','Plymouth'] # Non-repair depot
RD =['Manchester','Birmingham'] # Repair depot

days = [0,1,2,3,4,5] # Monday = 0, Tuesday = 1, ...  Saturday = 5
rentDays = [1,2,3]

d2w, demand = gp.multidict({
    ('Glasgow',0): 100,
    ('Glasgow',1): 150,
    ('Glasgow',2): 135,
    ('Glasgow',3): 83,
    ('Glasgow',4): 120,
    ('Glasgow',5): 230,
    ('Manchester',0): 250,
    ('Manchester',1): 143,
    ('Manchester',2): 80,
    ('Manchester',3): 225,
    ('Manchester',4): 210,
    ('Manchester',5): 98,
    ('Birmingham',0): 95,
    ('Birmingham',1): 195,
    ('Birmingham',2): 242,
    ('Birmingham',3): 111,
    ('Birmingham',4): 70,
    ('Birmingham',5): 124,
    ('Plymouth',0): 160,
    ('Plymouth',1): 99,
    ('Plymouth',2): 55,
    ('Plymouth',3): 96,
    ('Plymouth',4): 115,
    ('Plymouth',5): 80
})

#repairCap
depots, capacity = gp.multidict({
    ('Glasgow'): 0,
    ('Manchester'): 12,
    ('Birmingham'): 20,
    ('Plymouth'): 0
})

# Create a dictionary to capture
# pctRent: percentage of cars rented for r days
# cstMarginal: marginal cost for renting a car for r days
# prcSameD: price of renting a car r days and returning to same depot
# prcOtherD: price of renting a car r days and returning to another depot
rentDays, pctRent, costMarginal, priceSameD, priceOtherD = gp.multidict({
    (1): [0.55,20,50,70],
    (2): [0.20,25,70,100],
    (3): [0.25,30,120,150]
})

# Cost of owing a car per week.
cstOwn = 15

# Proportional damaged car fee
damagedFee = 10

# Create a dictionary to capture the proportion of cars rented at depot d to be returned to depot d2
d2d, pctFromToD = gp.multidict({
    ('Glasgow','Glasgow'): 0.6,
    ('Glasgow','Manchester'): 0.2,
    ('Glasgow','Birmingham'): 0.1,
    ('Glasgow','Plymouth'): 0.1,
    ('Manchester','Glasgow'): 0.15,
    ('Manchester','Manchester'): 0.55,
    ('Manchester','Birmingham'): 0.25,
    ('Manchester','Plymouth'): 0.05,
    ('Birmingham','Glasgow'): 0.15,
    ('Birmingham','Manchester'): 0.2,
    ('Birmingham','Birmingham'): 0.54,
    ('Birmingham','Plymouth'): 0.11,
    ('Plymouth','Glasgow'): 0.08,
    ('Plymouth','Manchester'): 0.12,
    ('Plymouth','Birmingham'): 0.27,
    ('Plymouth','Plymouth'): 0.53
})

# Create a dictionary to capture the transfer costs  of cars
d2d, cstFromToD = gp.multidict({
    ('Glasgow','Glasgow'): 0.001,
    ('Glasgow','Manchester'): 20,
    ('Glasgow','Birmingham'): 30,
    ('Glasgow','Plymouth'): 50,
    ('Manchester','Glasgow'): 20,
    ('Manchester','Manchester'): 0.001,
    ('Manchester','Birmingham'): 15,
    ('Manchester','Plymouth'): 35,
    ('Birmingham','Glasgow'): 30,
    ('Birmingham','Manchester'): 15,
    ('Birmingham','Birmingham'): 0.001,
    ('Birmingham','Plymouth'): 25,
    ('Plymouth','Glasgow'): 50,
    ('Plymouth','Manchester'): 35,
    ('Plymouth','Birmingham'): 25,
    ('Plymouth','Plymouth'): 0.001
})

# Proportion of undamaged and damaged cars returned
pctUndamaged = 0.9
pctDamaged = 0.1

# Build a list of tuples (depot, depot2) such that d != d2
list_d2notd = []

for d,d2 in d2d:
    if (d != d2):
        tp = d,d2
        list_d2notd.append(tp)

d2notd = gp.tuplelist(list_d2notd)

# Build a list of tuples (depot, depot2, day)
list_dd2t = []

for d,d2 in d2notd:
    for t in days:
        tp = d,d2,t
        list_dd2t.append(tp)

dd2t = gp.tuplelist(list_dd2t)

# Build a list of tuples (depot, rent_day)
list_dr = []

for d in depots:
    for r in rentDays:
        tp = d,r
        list_dr.append(tp)

dr = gp.tuplelist(list_dr)

# Build a list of tuples (depot, day, rent_days )
list_dtr = []

for d in depots:
    for t in days:
            for r in rentDays:
                tp = d,t,r
                list_dtr.append(tp)

dtr = gp.tuplelist(list_dtr)

# Build a list of tuples (depot, depot2, day, rent_days)
list_dd2tr = []

for d,d2 in d2notd:
    for t in days:
        for r in rentDays:
            tp = d,d2,t,r
            list_dd2tr.append(tp)


dd2tr = gp.tuplelist(list_dd2tr)

model = gp.Model('RentalCar1')

# Number of cars owned
n = model.addVar(name="cars")

# Number of undamaged cars
nu = model.addVars(d2w, name="UDcars")

# Number of damaged cars
nd = model.addVars(d2w, name="Dcars")

# Number of cars hired (rented) cannot exceed their demand
tr = model.addVars(d2w, ub=demand, name="Hcars")
#for d,t in d2w:
    #tr[d,t].lb = 1

# End inventory of undamaged cars
eu = model.addVars(d2w, name="EUDcars")

# End inventory of damaged cars
ed = model.addVars(d2w, name="EDcars")

# Number of undamaged cars transferred
tu = model.addVars(dd2t, name="TUDcars")

# Number of damaged cars transferred
td = model.addVars(dd2t, name="TDcars")

# Number of damaged cars repaired
rp = model.addVars(d2w, name="RPcars")

# Number of damaged cars repaired cannot exceed depot capacity
for d,t in d2w:
    rp[d,t].ub = capacity[d] #repair capacity

# Undamaged cars into a non-repair depot constraints (left hand side of balance equation -availability)

UDcarsNRD_L = model.addConstrs((gp.quicksum(pctUndamaged*pctFromToD[d2,d]*pctRent[r]*tr[d2,(t-r)%6 ] for d2,r in dr )
                              + gp.quicksum(tu.select('*',d,(t-1)%6)  )
                              + eu[d,(t-1)%6 ] == nu[d,t] for d in NRD for t in days ),
                             name="UDcarsNRD_L")

# Undamaged cars out of a non-repair depot constraints (right hand side of balance equation -requirements)

UDcarsNRD_R = model.addConstrs((tr[d,t]
                                + gp.quicksum(tu.select(d,'*',t ))
                                + eu[d,t] == nu[d,t] for d in NRD for t in days ), name='UDcarsNRD_R' )

# Undamaged cars into a repair depot constraints (left hand side of balance equation -availability)

UDcarsRD_L = model.addConstrs((gp.quicksum(pctUndamaged*pctFromToD[d2,d]*pctRent[r]*tr[d2,(t-r)%6 ] for d2,r in dr )
                              + gp.quicksum(tu.select('*',d,(t-1)%6)  ) + rp[d, (t-1)%6 ]
                              + eu[d,(t-1)%6 ] == nu[d,t] for d in RD for t in days ),
                             name="UDcarsRD_L")

# Undamaged cars out of a repair depot constraints (right hand side of balance equation -requirements)

UDcarsRD_R = model.addConstrs((tr[d,t]
                                + gp.quicksum(tu.select(d,'*',t ) )
                                + eu[d,t] == nu[d,t] for d in RD for t in days ), name='UDcarsRD_R' )

# Damaged cars into a non-repair depot constraints (left hand side of balance equation -availability)

DcarsNRD_L = model.addConstrs((gp.quicksum(pctDamaged*pctFromToD[d2,d]*pctRent[r]*tr[d2,(t-r)%6 ] for d2,r in dr )
                              + ed[d,(t-1)%6 ] == nd[d,t] for d in NRD for t in days ),
                             name="DcarsNRD_L")

# Damaged cars out of a non-repair depot constraints (right hand side of balance equation -requirements)

DcarsNRD_R = model.addConstrs(( gp.quicksum(td[d,d2,t] for d2 in RD )
                                + ed[d,t] == nd[d,t] for d in NRD for t in days ), name='DcarsNRD_R' )

# Damaged cars into a repair depot constraints (left hand side of balance equation -availability)

DcarsRD_L = model.addConstrs((gp.quicksum(pctDamaged*pctFromToD[d2,d]*pctRent[r]*tr[d2,(t-r)%6 ] for d2,r in dr )
                              + gp.quicksum(td[d2,d,(t-1)%6 ] for d2, dd in d2notd if (dd == d))
                              + ed[d,(t-1)%6 ] == nd[d,t] for d in RD for t in days ),
                             name="DcarsRD_L")

# Damaged cars out of a repair depot constraints (right hand side of balance equation -requirements)

DcarsND_R = model.addConstrs((rp[d,t] + gp.quicksum(td[d,d2,t ] for d2 in NRD )
                                + ed[d,t] == nd[d,t] for d in RD for t in days ), name='DcarsND_R' )

# Maximize profit objective function

model.setObjective((
    gp.quicksum(pctFromToD[d,d]*pctRent[r]*(priceSameD[r] - costMarginal[r] + damagedFee)*tr[d,t] for d,t,r in dtr )
    + gp.quicksum(pctFromToD[d,d2]*pctRent[r]*(priceOtherD[r]-costMarginal[r]+damagedFee)*tr[d,t] for d,d2,t,r in dd2tr)
    - gp.quicksum(cstFromToD[d,d2]*tu[d,d2,t] for d,d2,t in dd2t)
    - gp.quicksum(cstFromToD[d,d2]*td[d,d2,t] for d,d2,t in dd2t) - cstOwn*n ), GRB.MAXIMIZE)

# Verify model formulation

model.write('CarRental1.lp')

# Run optimization engine

model.optimize()

# Output report

# Total number of cars owned
print(f"The optimal number of cars to be owned is: {round(n.x)}.")

# Optimal profit
print(f"The optimal profit is: {'${:,.2f}'.format(round(model.objVal,2))}.")

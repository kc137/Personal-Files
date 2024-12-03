import pyomo.environ as pyo, gurobipy as gp
from pyomo.opt import SolverFactory

# list of depots and working days of a week

depots = ['Glasgow','Manchester','Birmingham','Plymouth']
NRD = ['Glasgow','Plymouth'] # Non-repair depot
RD =['Manchester','Birmingham'] # Repair depot

days = [1,2,3,4,5,6] # Monday = 0, Tuesday = 1, ...  Saturday = 5
rentDays = [1,2,3]

d2w, demand = gp.multidict({
    ('Glasgow',1): 100,
    ('Glasgow',2): 150,
    ('Glasgow',3): 135,
    ('Glasgow',4): 83,
    ('Glasgow',5): 120,
    ('Glasgow',6): 230,
    ('Manchester',1): 250,
    ('Manchester',2): 143,
    ('Manchester',3): 80,
    ('Manchester',4): 225,
    ('Manchester',5): 210,
    ('Manchester',6): 98,
    ('Birmingham',1): 95,
    ('Birmingham',2): 195,
    ('Birmingham',3): 242,
    ('Birmingham',4): 111,
    ('Birmingham',5): 70,
    ('Birmingham',6): 124,
    ('Plymouth',1): 160,
    ('Plymouth',2): 99,
    ('Plymouth',3): 55,
    ('Plymouth',4): 96,
    ('Plymouth',5): 115,
    ('Plymouth',6): 80
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

# Build a list of Tuples such that d != d2

list_d2notd = []

for d, d2 in d2d:
    if d != d2:
        tp = d, d2
        list_d2notd.append(tp)

d2notd = gp.tuplelist(list_d2notd)

# Build a list of Tuples (depot, depot2, day)

list_dd2t = []

for d, d2 in d2notd:
    for t in days:
        tp = d, d2, t
        list_dd2t.append(tp)
        
dd2t = gp.tuplelist(list_dd2t)

# Build a list of Tuples (depot, rent_day)
list_dr = []

for d in depots:
    for r in rentDays:
        tp = d, r
        list_dr.append(tp)

dr = gp.tuplelist(list_dr)

# Build a list of Tuples (depot, day, rent_day)

list_dtr = []

for d in depots:
    for t in days:
        for r in rentDays:
            tp = d, t, r
            list_dtr.append(tp)
dtr = gp.tuplelist(list_dtr)

# Build a list of Tuples (depot, depot2, day, rent_days)

list_dd2tr = []

for d, d2 in d2notd:
    for t in days:
        for r in rentDays:
            tp = d, d2, t, r
            list_dd2tr.append(tp)

dd2tr = gp.tuplelist(list_dd2tr)

# Model

model = pyo.ConcreteModel()

# Variables

# Owned Cars
model.n = pyo.Var(within = pyo.NonNegativeIntegers)
n = model.n

# Undamaged Cars
model.nu = pyo.Var(d2w, within = pyo.NonNegativeReals)
nu = model.nu

# Number of Damaged Cars
model.nd = pyo.Var(d2w, within = pyo.NonNegativeReals)
nd = model.nd

# Number of Rented Cars (Cannot exceed their demand)
model.tr = pyo.Var(d2w, within = pyo.NonNegativeReals)
tr = model.tr

# End Inventory of Undamaged Cars
model.eu = pyo.Var(d2w, within = pyo.NonNegativeReals)
eu = model.eu

# End Inventory of Damaged Cars
model.ed = pyo.Var(d2w, within = pyo.NonNegativeReals)
ed = model.ed

# Number of Undamaged Cars transferred
model.tu = pyo.Var(dd2t, within = pyo.NonNegativeReals)
tu = model.tu

# Number of Damaged Cars transferred
model.td = pyo.Var(dd2t, within = pyo.NonNegativeReals)
td = model.td

# Number of Damaged Cars Repaired
model.rp = pyo.Var(d2w, within = pyo.NonNegativeReals)
rp = model.rp

# Constraints

# Constraints for Undamaged Cars into a non-repair depot
model.c1 = pyo.ConstraintList(name = "Undamaged cars into non-repair Depot")

for d in NRD:
    for t in days:
        model.c1.add(
            pyo.quicksum(
                pctUndamaged*pctFromToD[d2, d]*pctRent[r]*tr[d2, abs(t-r)+1] for d2, r in dr
                ) + 
            pyo.quicksum(
                tu[d2, d, t] for d2 in depots if d2 != d
                ) + 
            eu[d, t] == nu[d, (t+1)%6 if t+1 > 6 else t+1]
            )

for d in NRD:
    for t in days:
        model.c1.add(tr[d, t] + 
                     pyo.quicksum(tu[d, d2, t] for d2 in depots if d2 != d) + 
                     eu[d, t] == nu[d, t]
                     )

# Constraints for Undamaged Cars into a repair depot

model.c2 = pyo.ConstraintList(name = "Undamaged cars into repair Depot")

for d in RD:
    for t in days:
        model.c2.add(
            pyo.quicksum(
                pctUndamaged*pctFromToD[d2, d]*pctRent[r]*tr[d2, abs(t-r)+1] for d2, r in dr
                ) + 
            pyo.quicksum(
                tu[d2, d, t] for d2 in depots if d2 != d
                ) + 
            rp[d, t] + 
            eu[d, t] == nu[d, (t+1)%6 if t+1 > 6 else t+1]
            )

for d in RD:
    for t in days:
        model.c2.add(tr[d, t] + 
                     pyo.quicksum(tu[d, d2, t] for d2 in depots if d2 != d) + 
                     eu[d, t] == nu[d, t]
                     )

# Constraints for Damaged Cars into a non-repair depot

model.c3 = pyo.ConstraintList(name = "Damaged cars into non-repair Depot")

for d in NRD:
    for t in days:
        model.c3.add(
            pyo.quicksum(
                pctDamaged*pctFromToD[d2, d]*pctRent[r]*tr[d2, abs(t-r)+1] for d2, r in dr
                ) + 
            ed[d, t] == nd[d, (t+1)%6 if t+1 > 6 else t+1]
            )

for d in NRD:
    for t in days:
        model.c3.add(
            pyo.quicksum(td[d, d2, t] for d2 in RD) + 
            ed[d, t] == nd[d, t]
            )

# Constraints for Damaged Cars into a repair depot

model.c4 = pyo.ConstraintList(name = "Damaged cars into repair Depot")

for d in RD:
    for t in days:
        model.c4.add(
            pyo.quicksum(
                pctDamaged*pctFromToD[d2, d]*pctRent[r]*tr[d2, abs(t-r)+1] for d2, r in dr
                ) + 
            pyo.quicksum(
                td[d, d2, t] for d2, dd in d2notd if dd == d
                ) + 
            ed[d, t] == nd[d, (t+1)%6 if t+1 > 6 else t+1]
            )

for d in RD:
    for t in days:
        model.c4.add(
            rp[d, t] + 
            pyo.quicksum(td[d, d2, t] for d2 in NRD) + 
            ed[d, t] == nd[d, t]
            )

# Depot Capacity

model.cap = pyo.ConstraintList()

for d in depots:
    for t in days:
        model.cap.add(rp[d, t] <= capacity[d])
        
# Depot Demand

model.dep_dem = pyo.ConstraintList()

for d in depots:
    for t in days:
        model.dep_dem.add(tr[d, t] <= demand[d, t])
        
# Total Cars

model.c5 = pyo.ConstraintList()

model.c5.add(
    pyo.quicksum(
        (0.25*tr[d, 1] + 0.45*tr[d, 2] + nu[d, 3] + nd[d, 3] for d in depots)) == n
    )

# Objective Function

def obj_fn(model):
    return (pyo.quicksum(pctFromToD[d, d]*pctRent[r]*
                         (priceSameD[r] - costMarginal[r] + damagedFee)*
                         tr[d, t] for d, t, r in dtr) + 
            pyo.quicksum(pctFromToD[d, d2]*pctRent[r]*
                         (priceOtherD[r] - costMarginal[r] + damagedFee)*
                         tr[d, t] for d, d2, t, r in dd2tr) - 
            pyo.quicksum(cstFromToD[d, d2]*(tu[d, d2, t]) for d, d2, t in dd2t) - 
            pyo.quicksum(cstFromToD[d, d2]*(td[d, d2, t]) for d, d2, t in dd2t)
            - cstOwn*n)

"""
model.setObjective((
    gp.quicksum(pctFromToD[d,d]*pctRent[r]*(priceSameD[r] - costMarginal[r] + damagedFee)*tr[d,t] for d,t,r in dtr )
    + gp.quicksum(pctFromToD[d,d2]*pctRent[r]*(priceOtherD[r]-costMarginal[r]+damagedFee)*tr[d,t] for d,d2,t,r in dd2tr)
    - gp.quicksum(cstFromToD[d,d2]*tu[d,d2,t] for d,d2,t in dd2t)
    - gp.quicksum(cstFromToD[d,d2]*td[d,d2,t] for d,d2,t in dd2t) - cstOwn*n ), GRB.MAXIMIZE)
"""

model.obj = pyo.Objective(rule = obj_fn, sense = pyo.maximize)

# Solution

sol = SolverFactory("cplex")
sol.options["timelimit"] = 15
res = sol.solve(model)

# Printing the Solution

print(f"The number of cars that should be owned : {n()}-Cars")
print(f"The total profit for the Car Rental Company : {model.obj()} $.")
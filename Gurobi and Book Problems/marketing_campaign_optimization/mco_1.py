import pyomo.environ as pyo, gurobipy as gp
from pyomo.opt import SolverFactory

M = 10000

# Sets

products = ['p1', 'p2']
clusters = ['k1', 'k2']

# Expected Profit

cp, expected_profit = gp.multidict({
    ('k1', 'p1'): 2000,
    ('k1', 'p2'): 1000,
    ('k2', 'p1'): 3000,
    ('k2', 'p2'): 2000
})

# Expected Cost

cp, expected_cost = gp.multidict({
    ('k1', 'p1'): 200,
    ('k1', 'p2'): 100,
    ('k2', 'p1'): 300,
    ('k2', 'p2'): 200
})

# Number of Customers

clusters, number_customers = gp.multidict({
    ('k1'): 5,
    ('k2'): 5
})

# Minimum no. of offers

products, min_offers = gp.multidict({
    ('p1'): 2,
    ('p2'): 2
})

# Corporate Hurdle-Rate

R = 0.2

# Budget

budget = 200

# Model

model = pyo.ConcreteModel(name = "Tactical Model")

# Variables

# Allocation of product offers to customers in clusters.

model.y = pyo.Var(cp, within = pyo.NonNegativeReals)
y = model.y

# Budget Correction

model.z = pyo.Var(within = pyo.NonNegativeReals)
z = model.z

# Constraints

# Number of offers

def max_offers(model, k):
    return pyo.quicksum(y[k, j] for j in products) <= number_customers[k]
model.c1 = pyo.Constraint(clusters, rule = max_offers)

# Budget

def budget_cons(model):
    return pyo.quicksum(expected_cost[k, j]*y[k, j] 
                        for k in clusters 
                        for j in products) <= budget + z
model.c2 = pyo.Constraint(rule = budget_cons)

# Offers Limit

def min_offers_cons(model, j):
    return pyo.quicksum(y[k, j] for k in clusters) >= min_offers[j]
model.c3 = pyo.Constraint(products, rule = min_offers_cons)

# Return on Investment

def roi_cons(model):
    return (pyo.quicksum(expected_profit[k, j]*y[k, j] 
                         for k in clusters 
                         for j in products) 
            >= (1 + R)*pyo.quicksum(expected_cost[k, j] 
                                    for k in clusters 
                                    for j in products))
model.c4 = pyo.Constraint(rule = roi_cons)

# Objective Function

def obj_fn(model):
    return pyo.quicksum(expected_profit[k, j]*y[k, j] 
                        for k in clusters 
                        for j in products) - M*z
model.obj = pyo.Objective(rule = obj_fn, sense = pyo.maximize)

# Solution

sol = SolverFactory("cplex")
res = sol.solve(model)

# Printing the Results

print(res)

total_profit = 0
total_cost = 0

for k, p in cp:
    if y[k, p]():
        print(f"The number of customers in cluster-{k} that gets a product-{p} : {y[k, p]()}")
        total_profit += expected_profit[k, p]*y[k, p]()
        total_cost += expected_cost[k, p]*y[k, p]()

optimal_roi = round(100*total_profit/total_cost, 3)
min_roi = round(100*(1 + R), 3)

print(f"Total expected profit : ${total_profit}")
print(f"Total expected cost : ${total_cost}")
print(f"The increased correction in the campaign budget : ${z()}")
print(f"Optimal ROI : {optimal_roi}%")
print(f"Minimum ROI : {min_roi}%")

"""Operational Model Formulation"""

# Sets

customers = ['c1', 'c2','c3','c4','c5','c6','c7','c8','c9','c10']

# Params

# Expected profit from a product offering for each customer in each cluster

ccp, customer_profit = gp.multidict({
    ('k1', 'c1', 'p1'): 2050,
    ('k1', 'c1', 'p2'): 1050,
    ('k1', 'c2', 'p1'): 1950,
    ('k1', 'c2', 'p2'): 950,
    ('k1', 'c3', 'p1'): 2000,
    ('k1', 'c3', 'p2'): 1000,
    ('k1', 'c4', 'p1'): 2100,
    ('k1', 'c4', 'p2'): 1100,
    ('k1', 'c5', 'p1'): 1900,
    ('k1', 'c5', 'p2'): 900,
    ('k2', 'c6', 'p1'): 3000,
    ('k2', 'c6', 'p2'): 2000,
    ('k2', 'c7', 'p1'): 2900,
    ('k2', 'c7', 'p2'): 1900,
    ('k2', 'c8', 'p1'): 3050,
    ('k2', 'c8','p2'): 2050,
    ('k2', 'c9', 'p1'): 3100,
    ('k2', 'c9', 'p2'): 3100,
    ('k2', 'c10', 'p1'): 2950,
    ('k2', 'c10', 'p2'): 2950   
})

# Customer cost of offering a product at a cluster

ccp, customer_cost = gp.multidict({
    ('k1', 'c1', 'p1'): 205,
    ('k1', 'c1', 'p2'): 105,
    ('k1', 'c2', 'p1'): 195,
    ('k1', 'c2', 'p2'): 95,
    ('k1', 'c3', 'p1'): 200,
    ('k1', 'c3', 'p2'): 100,
    ('k1', 'c4', 'p1'): 210,
    ('k1', 'c4', 'p2'): 110,
    ('k1', 'c5', 'p1'): 190,
    ('k1', 'c5', 'p2'): 90,
    ('k2', 'c6', 'p1'): 300,
    ('k2', 'c6', 'p2'): 200,
    ('k2', 'c7', 'p1'): 290,
    ('k2', 'c7', 'p2'): 190,
    ('k2', 'c8', 'p1'): 305,
    ('k2', 'c8','p2'): 205,
    ('k2', 'c9', 'p1'): 310,
    ('k2', 'c9', 'p2'): 310,
    ('k2', 'c10', 'p1'): 295,
    ('k2', 'c10', 'p2'): 295   
})

# Model

model = pyo.ConcreteModel(name = "Operational Model")

# Variables

model.x = pyo.Var(ccp, within = pyo.Binary)
x = model.x

# Constraints

# Product Offers

def allocate_offers(model, k, j):
    return (pyo.quicksum(x[k, i, j] 
                         for kk, i, jj in ccp 
                         if (kk == k and jj == j)) 
            == int(y[k, j]()))
model.c1 = pyo.Constraint(clusters, products, rule = allocate_offers)

# Offers Limit

# limit on the number of offers to each customer in a cluster.

ki = [('k1', 'c1'), 
      ('k1', 'c2'), 
      ('k1', 'c3'),
      ('k1', 'c4'), 
      ('k1', 'c5'), 
      ('k2', 'c6'), 
      ('k2', 'c7'), 
      ('k2', 'c8'), 
      ('k2', 'c9'), 
      ('k2', 'c10')]


def at_most_one(model, k, i):
    return pyo.quicksum(x[k, i, j] 
                        for kk, ii, j in ccp 
                        if (kk == k and ii == i))  <= 1
model.c2 = pyo.Constraint(ki, rule = at_most_one)

# Objective Function

def obj_fn(model):
    return pyo.quicksum(customer_profit[k, i, j]*x[k, i, j] 
                        for k, i, j in ccp)
model.obj = pyo.Objective(rule = obj_fn, sense = pyo.maximize)

# Solution

sol = SolverFactory("cplex")
res = sol.solve(model)

# Printing the Solution

# print(res)

assignments_1, assignments_2 = 0, 0
total_cust_cost, total_cust_profit = 0, 0

for k, i, j in ccp:
    if x[k, i, j]() and x[k, i, j]() >= 0.9:
        print(f"Customer-{i} in Cluster-{k} gets an offer of product-{j}")
        print(f"The expected profit is {customer_profit[k, i, j]}")
        print(f"The expected cost is {customer_cost[k, i, j]}")
        assignments_1 += 1 if (k == "k1" and x[k, i, j]() >= 0.9) else 0
        assignments_2 += 1 if (k == "k2" and x[k, i, j]() >= 0.9) else 0
        total_cust_profit += x[k, i, j]()*customer_profit[k, i, j]
        total_cust_cost += x[k, i, j]()*customer_cost[k, i, j]
        
print(f"Number of assignments in cluster-k1 : {assignments_1}")
print(f"Number of assignments in cluster-k2 : {assignments_2}")

print(f"\nOptimal customer profit : {total_cust_profit}")
print(f"\nOptimal customer cost : {total_cust_cost}")
print(f"\nThe increased correction in the campaign budget : ${z()}")
print(f"\nOptimal ROI : {optimal_roi}%")
print(f"\nMinimum ROI : {min_roi}%")








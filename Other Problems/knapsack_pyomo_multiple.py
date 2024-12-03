import pyomo.environ as pyo
from pyomo.opt import SolverFactory

# Model

model = pyo.ConcreteModel()

# Sets and Params

N = 14

space_limit = 10

products_list = [('Refrigerator A', 0.751, 999.90, 1), 
            ('Cell phone', 0.0000899, 2199.12, 5), 
            ('TV 55', 0.400, 4346.99, 2), 
            ('TV 50', 0.290, 3999.90, 3), 
            ('TV 42', 0.200, 2999.00, 4), 
            ('Notebook A', 0.00350, 2499.90, 1), 
            ('Ventilador', 0.496, 199.90, 10), 
            ('Microwave A', 0.0424, 308.66, 2), 
            ('Microwave B', 0.0544, 429.90, 5), 
            ('Microwave C', 0.0319, 299.29, 3), 
            ('Refrigerator B', 0.635, 849.00, 2), 
            ('Refrigerator C', 0.870, 1199.89, 6), 
            ('Notebook B', 0.498, 1999.90, 2), 
            ('Notebook C', 0.527, 3999.00, 1)]

names  = []
spaces = []
prices = []
quantities = []

for name, space, price, qty in products_list:
    names.append(name)
    spaces.append(space)
    prices.append(price)
    quantities.append(qty)

model.products = pyo.Set(initialize = names)
products = model.products

# Variables

model.x = pyo.Var(products, within = pyo.NonNegativeIntegers)
x = model.x

# Constraints

def capacity_cons(model):
    return pyo.quicksum(x[products.at(p+1)]*spaces[p] 
                        for p in range(N)) <= space_limit
model.c1 = pyo.Constraint(rule = capacity_cons)

model.c2 = pyo.ConstraintList()
for p in range(N):
    model.c2.add(x[products.at(p+1)] <= quantities[p])

# model.c2 = pyo.ConstraintList()
# cons_2 = [0, 1, 0, 1, 1, 1, 1, 1, 0, 1, 0, 1, 0, 1]

# for p in range(N):
#     if cons_2[p]:
#         model.c2.add(x[products.at(p+1)] == 1)
#     else:
#         model.c2.add(x[products.at(p+1)] == 0)


# Objective Function

def obj_fn(model):
    return pyo.quicksum(x[products.at(p+1)]*prices[p] 
                        for p in range(N))
model.obj = pyo.Objective(rule = obj_fn, sense = pyo.maximize)

# Solution

sol = SolverFactory("cplex")
res = sol.solve(model)

# Printing the Solution

print(res)

for p in products:
    if x[p]() and x[p]() >= 0.9:
        print(f"x[{p}] = {x[p]()}")
        print(f"Product-{p} is selected for transportation")

print(f"Total Price : {model.obj()}$")
    
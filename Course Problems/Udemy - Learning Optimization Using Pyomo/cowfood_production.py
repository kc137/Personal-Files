import pyomo.environ as pyo
from pyomo.opt import SolverFactory

model = pyo.ConcreteModel()

foods = {
    1 : "Granules", 
    2 : "Powder"
    }

raw_materials = {
    1 : "Oats", 
    2 : "Maize", 
    3 : "Molasses"
    }

nutrients = {
    1 : "Protein", 
    2 : "Lipids", 
    3 : "Fiber"
    }

# Sets

model.food = pyo.RangeSet(1, 2)
model.raw_mat = pyo.RangeSet(1, 3)
model.nutri = pyo.RangeSet(1, 3)
model.processes = pyo.RangeSet(1, 4)

# Params

cost_list = [0.13, 0.17, 0.12]
model.raw_mat_cost = pyo.Param(model.raw_mat, within = pyo.Any, 
                       initialize = {n : cost_list[n-1] for n in model.raw_mat})

content_list = [
    [13.6, 7.1, 7.0], 
    [4.1, 2.4, 3.7], 
    [5.0, 0.3, 25]
    ]
# content_list = [[content_list1[j][i] for j in range(len(content_list1))] 
#                 for i in range(len(content_list1))]
model.content_in_raw_mat = pyo.Param(
    model.raw_mat, model.nutri, 
    within = pyo.Any, 
    initialize = {(i, j) : content_list[i-1][j-1] 
                  for i in model.raw_mat
                  for j in model.nutri}
    )

content_req_list = [9.5, 2, 6]
model.req_content = pyo.Param(model.nutri, within = pyo.Any, 
                              initialize = {n : content_req_list[n-1] 
                                            for n in model.nutri})

available_raw_mat = [11900, 23500, 750]
model.max_raw_mat = pyo.Param(model.raw_mat, within = pyo.Any, 
                              initialize = {n : available_raw_mat[n-1] 
                                            for n in model.raw_mat})
food_demand = [9000, 12000]
model.demand = pyo.Param(model.food, within = pyo.Any, 
                         initialize = {n : food_demand[n-1]
                                       for n in model.food})

prod_costs = [0.25, 0.05, 0.42, 0.17]
model.costs = pyo.Param(model.processes, within = pyo.Any, 
                        initialize = {n : prod_costs[n-1] 
                                      for n in model.processes})

# Variables

model.x = pyo.Var(model.raw_mat, model.food, 
                  within = pyo.NonNegativeReals)
x = model.x

model.y = pyo.Var(model.food, 
                  within = pyo.NonNegativeReals)
y = model.y

# Constraints

def raw_mat_and_food(model, f):
    return sum(x[r, f] for r in model.raw_mat) == y[f]
model.c1 = pyo.Constraint(model.food, rule = raw_mat_and_food)

def raw_mat_food_nutri(model, f, c):
    if c != 3:
        return (sum(x[r, f]*model.content_in_raw_mat[r, c] for r in model.raw_mat) >= 
                y[f]*model.req_content[c])
    else:
        return (sum(x[r, f]*model.content_in_raw_mat[r, c] for r in model.raw_mat) <= 
                y[f]*model.req_content[c])
model.c2 = pyo.Constraint(model.food, model.nutri, rule = raw_mat_food_nutri)

def demand(model, f):
    return model.y[f] >= model.demand[f]
model.c3 = pyo.Constraint(model.food, rule = demand)

def availability(model, r):
    return sum(x[r, f] for f in model.food) <= model.max_raw_mat[r]
model.c4 = pyo.Constraint(model.raw_mat, rule = availability)

# Objective Function

def obj_fn(model):
    raw_mat_cost = sum(x[r, f]*model.raw_mat_cost[r] 
                        for r in model.raw_mat 
                        for f in model.food)
    
    grinding = sum(model.costs[1]*x[r, f] for r in model.raw_mat 
                    for f in model.food if r != 3)
    
    blending = sum(model.costs[2]*x[r, f] for r in model.raw_mat 
                    for f in model.food)
    
    granulating = sum(model.costs[3]*x[r, 1] for r in model.raw_mat)
    
    sieving = sum(model.costs[4]*x[r, 2] for r in model.raw_mat)
    
    return raw_mat_cost + grinding + granulating + blending + sieving

# def obj_fn(model):
#     expr = 0
#     for r in model.raw_mat:
#         for f in model.food:
#             expr += model.costs[r]*model.x[r, f]
#         for f in model.food:
#             for r in model.raw_mat:
#                 if r != 3:
#                     expr += 0.25*x[r, f]
#         for r in model.raw_mat:
#             for f in model.food:
#                 expr += 0.05*x[r, f]
#         for r in model.raw_mat:
#             expr += 0.42*x[r, 1] + 0.17*x[r, 2]
#         return expr
    
model.obj = pyo.Objective(rule = obj_fn, sense = pyo.minimize)

# Solution

sol = SolverFactory("cplex")
res = sol.solve(model)

# Printing the Solution

print(f"Total minimized cost : {model.obj()} $")

for r in model.raw_mat:
    for f in model.food:
        print(f"x[{raw_materials[r]}, {foods[f]}] : {x[r, f]()}")

for f in model.food:
    print(f"y[{foods[f]}] : {y[f]()}")

for r in model.raw_mat:
    print(f"x[{raw_materials[r]}] : {sum(x[r, f]() for f in model.food)}")
    
    
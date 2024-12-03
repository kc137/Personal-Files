import pyomo.environ as pyo
from pyomo.opt import SolverFactory

model = pyo.ConcreteModel()

# Sets

model.patterns = pyo.RangeSet(1, 16)
model.sizes = pyo.RangeSet(1, 4)
sizes_dict = {
    1 : "36 X 50", 
    2 : "24 X 36", 
    3 : "20 X 60", 
    4 : "18 X 30"
    }

# Parameters

cut_matrix = [
    [1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
    [2, 1, 0, 2, 1, 0, 3, 2, 1, 0, 5, 4, 3, 2, 1, 0], 
    [0, 0, 0, 2, 2, 2, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0], 
    [0, 1, 3, 0, 1, 3, 0, 2, 3, 5, 0, 1, 3, 5, 6, 8]
    ]

model.cut_sizes = pyo.Param(model.sizes, 
                            model.patterns, 
                            within = pyo.Any, 
                            initialize = {
                                (i, j) : cut_matrix[i-1][j-1] 
                                for i in model.sizes 
                                for j in model.patterns
                                })

demand_list = [8, 13, 5, 15]
model.demands = pyo.Param(model.sizes, 
                          within = pyo.Any, 
                          initialize = {
                              n : demand_list[n-1] for n in model.sizes
                              })

model.cost = pyo.Param(model.patterns, 
                       within = pyo.Any, 
                       initialize = {p : 1 for p in model.patterns})

# Variables

model.x = pyo.Var(model.patterns, within = pyo.NonNegativeIntegers)
x = model.x

# Constraints

def demand(model, s):
    return sum(x[p]*model.cut_sizes[s, p] for p in model.patterns) >= model.demands[s]
model.c1 = pyo.Constraint(model.sizes, rule = demand)

# Objective Function

def obj_fn(model):
    return sum(x[p]*model.cost[p] for p in model.patterns)
model.obj = pyo.Objective(rule = obj_fn, sense = pyo.minimize)

# Solution

sol = SolverFactory("cplex")
res = sol.solve(model)

# Printing the Solution

for p in model.patterns:
    if x[p]() > 0.5:
        print(f"Pattern-{p} is cut {x[p]()} times.")
    else:
        print(f"Pattern-{p} is not cut.")
    
print(f"Total large sheets used : {model.obj()} sheets.")
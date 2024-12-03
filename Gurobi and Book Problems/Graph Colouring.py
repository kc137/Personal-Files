import pyomo.environ as pyo
from pyomo.opt import SolverFactory

model = pyo.ConcreteModel()

# Sets and Parameters

model.vertices = pyo.Set(initialize = ['Ar' , 'Bo' , 'Br' , 'Ch' , 'Co' , 'Ec' , 'Fg' , 'Gu' , 'Pa' , 'Pe' , 'Su' , 'Ur' , 'Ve'])
vertices = model.vertices

model.edges = pyo.Set(initialize = [("Fg", "Su"), ("Fg", "Br"), ("Su", "Gu"), ("Su", "Br"), ("Gu", "Ve"), 
                 ("Gu", "Br"), ("Ve", "Co"), ("Ve", "Br"), ("Co", "Ec"), ("Co", "Pe"), 
                 ("Co", "Br"), ("Ec", "Pe"), ("Pe", "Ch"), ("Pe", "Bo"), ("Pe", "Br"), 
                 ("Ch", "Ar"), ("Ch", "Bo"), ("Ar", "Ur"), ("Ar", "Br"), ("Ar", "Pa"), 
                 ("Ar", "Bo"), ("Ur", "Br"), ("Bo", "Pa"), ("Bo", "Br"), ("Pa", "Br")])
edges = model.edges

N = 4
colors = range(1, N+1)

# Variables

model.x = pyo.Var(vertices, colors, domain = pyo.Binary)
x = model.x

model.y = pyo.Var(domain = pyo.NonNegativeReals)
y = model.y

# Constraints

def Cons1(model, vertices):
    return sum(x[vertices, c] for c in colors) == 1
model.C1 = pyo.Constraint(vertices, rule = Cons1)

model.C2 = pyo.ConstraintList()
# for i in range(1, len(edges)):
#     for c in colors:
#         model.C2.add(x[edges[i][0], c] + x[edges[i][1], c] <= 1)

for v1, v2 in edges:
    for c in colors:
        model.C2.add(x[v1, c] + x[v2, c] <= 1)

model.C3 = pyo.ConstraintList()

for v in vertices:
    for c in colors:
        model.C3.add(y >= c*x[v, c])

# Objective Function

model.Obj = pyo.Objective(expr = y, sense = pyo.minimize)

# Solution

sol = SolverFactory("cplex")
res = sol.solve(model)

for v1, v2 in edges:
    for c in colors:
        if x[v1, c]():
            print(f"The colour on vertice {v1} is {c}")
    for c in colors:
        if x[v2, c]():
            print(f"The colour on vertice {v2} is {c}")






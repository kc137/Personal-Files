import pyomo.environ as pyo, gurobipy as gp, math, matplotlib.pyplot as plt, \
    matplotlib, random, networkx as nx
from pyomo.opt import SolverFactory
matplotlib.use("tkagg")

#  Create a dictionary to capture the farm coordinates (10 miles) and collection requirements (1,000).

farms, coordinates, collect  = gp.multidict({
    0: [(0,0),0],
    1: [(-3,3),5],
    2: [(1,11),4],
    3: [(4,7),3],
    4: [(-5,9),6],
    5: [(-5,-2),7],
    6: [(-4,-7),3],
    7: [(6,0),4],
    8: [(3,-6),6],
    9: [(-1,-3),5],
    10: [(0,-6),4],
    11: [(6,4),7], 
    12: [(2,5),3],
    13: [(-2,8),4],
    14: [(6,10),5],
    15: [(1,8),6],
    16: [(-3,1),8],
    17: [(-6,5),5],
    18: [(2,9),7],
    19: [(-6,-5),6],
    20: [(5,-4),6]
})

# List of farms with depot
farms = [*range(1, 22)]

# List of farms that are visited everyday
everyday_farms = [*range(1, 11)]

# List of farms that are visited every other day
otherday_farms = [*range(11, 22)]

# Day-type
day_type = [1, 2]

# Tanker Capacity (1000 tonnes)
tanker_cap = 80

# Dictionary for Distances

dist = {(p1, p2) : math.hypot(coordinates[p1-1][0] - coordinates[p2-1][0], 
                              coordinates[p1-1][1] - coordinates[p2-1][1]) 
        if p1 != p2
        else 0
        for p1 in farms 
        for p2 in farms 
        }

# Every day farms requirements
everyDayReq = 0
for i in everyday_farms:
    everyDayReq += collect[i]

# Model

model = pyo.ConcreteModel()

# Variables

model.x = pyo.Var(farms, farms, day_type, within = pyo.Binary)
x = model.x

model.y = pyo.Var(otherday_farms, day_type, within = pyo.Binary)
y = model.y

model.u = pyo.Var(farms, within = pyo.NonNegativeReals)
u = model.u

# Constraints

def visit_1(model, i, k):
    return pyo.quicksum(x[i, j, k] 
                        for j in farms 
                        if i != j) == 1
model.c1 = pyo.Constraint(everyday_farms, day_type, rule = visit_1)

def visit_2(model, i, k):
    return pyo.quicksum(x[j, i, k] 
                        for j in farms 
                        if i != j) == 1
model.c2 = pyo.Constraint(everyday_farms, day_type, rule = visit_2)

def flow_1(model, i, k):
    return (pyo.quicksum(x[i, j, k] 
                        for j in farms 
                        if i != j) 
            == pyo.quicksum(x[j, i, k] 
                            for j in farms 
                            if i != j)
            )
model.c3 = pyo.Constraint(otherday_farms, day_type, rule = flow_1)

def flow_2(model, i, k):
    return pyo.quicksum(x[j, i, k] 
                        for j in farms 
                        if i != j) == y[i, k]
model.c4 = pyo.Constraint(otherday_farms, day_type, rule = flow_2)

def capacity(model, k):
    return (everyDayReq + pyo.quicksum(y[i, k]*collect[i-1] 
                                       for i in otherday_farms) 
            <= tanker_cap)
model.c5 = pyo.Constraint(day_type, rule = capacity) 

def farms_visit_limit(model, i):
    return pyo.quicksum(y[i, k] for k in day_type) == 1
model.c6 = pyo.Constraint(otherday_farms, rule = farms_visit_limit)

model.sub_tour = pyo.ConstraintList()

# model.sub_tour.add(y[11, 1] == 1)

for i in farms[1:]:
    for j in farms[1:]:
        for k in day_type:
            if i != j:
                model.sub_tour.add(
                    u[i] - u[j] + farms[-1]*x[i, j, k] <= farms[-1] - 1
                    )

# Objective Function

def obj_fn(model):
    return pyo.quicksum(
        x[i, j, k]*dist[i, j] 
        for i in farms 
        for j in farms 
        for k in day_type 
        if i != j
        )
model.obj = pyo.Objective(rule = obj_fn, sense = pyo.minimize)

# Solution

sol = SolverFactory("cplex")
sol.options["timelimit"] = 10
res = sol.solve(model)

# Printing the Solution

print(res)

visits = {day : [] for day in day_type}
node_dict = {day : [] for day in day_type}

for i in farms:
    for j in farms:
        for k in day_type:
            if i != j and x[i, j, k]() and x[i, j, k]() >= 0.9:
                # print(f"x[{i}, {j}, {k}] = {x[i, j, k]()}")
                visits[k].append((i, j))
                if i != 1:
                    node_dict[k].append(i)

# colors = ["#" + "".join(random.choice("0123456789ABCDEF") for _ in range(6)) 
#           for _ in range(2)]
colors = ["red", "blue"]

node_color_dict = {1 : "black"}

for node in farms[1:]:
    if node <= 10:
        node_color_dict[node] = colors[0]
    else:
        node_color_dict[node] = colors[1]

# print(colors)

for day in visits:
    for p1, p2 in visits[day]:
        pts = [coordinates[p1-1], coordinates[p2-1]]
        # plt.scatter(pts[0][0], pts[0][1], c = colors[day-1])
        # plt.scatter(pts[1][0], pts[1][1], c = colors[day-1])
        plt.plot(*zip(*pts), c = colors[day-1])

G = nx.Graph()

G.add_nodes_from(farms)

for node, pos in coordinates.items():
    G.nodes[node+1]["pos"] = pos

pos = {node : G.nodes[node]["pos"] for node in G.nodes()}

nx.draw(G, pos = pos, node_color = node_color_dict.values(), with_labels = True, 
        font_color = "white")
plt.show()


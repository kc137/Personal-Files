import pyomo.environ as pyo, matplotlib.pyplot as plt, random, matplotlib, networkx as nx
from pyomo.opt import SolverFactory
from rc101_100_data import matrix, time_array, demands, capacity, service_time, coords
matplotlib.use("tkagg")

NC = len(matrix)
NV = 25
M = 2000
T = time_array[0][1]

model = pyo.ConcreteModel()

# Sets and Params

model.N = pyo.RangeSet(1, NC)
model.C = pyo.RangeSet(2, NC)

# Variables

model.x = pyo.Var(model.N, model.N, within = pyo.Binary)
x = model.x

model.q = pyo.Var(model.N, within = pyo.NonNegativeReals)
q = model.q

model.t = pyo.Var(model.N, within = pyo.NonNegativeReals)
t = model.t

# Constraints

def once(model, j):
    return pyo.quicksum(x[i, j] for i in model.N if i != j) == 1
model.c1 = pyo.Constraint(model.C, rule = once)

def flow(model, j):
    return pyo.quicksum(x[i, j] for i in model.N if i != j) == \
            pyo.quicksum(x[j, i] for i in model.N if i != j)
model.c2 = pyo.Constraint(model.C, rule = flow)

# def demand(model):
#     return pyo.quicksum(x[i, j]*demands[j-1] 
#                         for i in model.N 
#                         for j in model.C if i != j) <= capacity
# model.c3 = pyo.Constraint(rule = demand)

def demand(model, i, j):
    if i != j:
        return q[i] + demands[j-1] <= q[j] + capacity*(1 - x[i, j])
    else:
        return pyo.Constraint.Skip
model.c3 = pyo.Constraint(model.N, model.C, rule = demand)

model.depot = pyo.ConstraintList()
model.depot.add(pyo.quicksum(x[1, j] for j in model.C) >= 1)
model.depot.add(pyo.quicksum(x[1, j] for j in model.C) <= NV)

def time_windows(model, i, j):
    if i != j:
        return t[i] + matrix[i-1][j-1] + service_time <= t[j] + T*(1 - x[i, j])
    else:
        return pyo.Constraint.Skip
model.c5 = pyo.Constraint(model.N, model.C, rule = time_windows)

# def time_windows(model, i, j):
#     if i != j:
#         return t[i] + matrix[i-1][j-1] + service_time <= t[j] + M*(1 - x[i, j])
#     else:
#         return pyo.Constraint.Skip
# model.c5 = pyo.Constraint(model.C, model.N, rule = time_windows)

def service1(model, j):
    return t[j] >= time_array[j-1][0]
model.c6 = pyo.Constraint(model.C, rule = service1)

def service2(model, j):
    return t[j] <= time_array[j-1][1]
model.c7 = pyo.Constraint(model.C, rule = service2)

# def service1(model, j):
#     return t[j] >= time_array[j-1][0]
# model.c6 = pyo.Constraint(model.N, rule = service1)

# def service2(model, j):
#     return t[j] <= time_array[j-1][1]
# model.c7 = pyo.Constraint(model.N, rule = service2)

def total_veh(model):
    return pyo.quicksum(x[1, j] for j in model.C) ==\
           pyo.quicksum(x[j, 1] for j in model.C)
model.c8 = pyo.Constraint(rule = total_veh)

# Objective Function

def obj_fn(model):
    return pyo.quicksum(x[i, j]*matrix[i-1][j-1] 
                        for i in model.N 
                        for j in model.N if i != j)
model.obj = pyo.Objective(rule = obj_fn, sense = pyo.minimize)

# Solution

sol = SolverFactory("cplex")
sol.options["timelimit"] = 60
res = sol.solve(model)

# Printing the Solution

# print(f"The total distance travelled by all vehicles : {pyo.value(model.obj)} km.")
print(f"The total distance travelled by all vehicles : {model.obj()} km.")

origins = []

for j in model.C:
    if x[1, j]() and x[1, j]() >= 0.9:
        origins.append((1, j))

arcs = []

routes = {v + 1 : [origins[v]] for v in range(len(origins))}

for i in model.N:
    for j in model.N:
        if i != j and x[i, j]() and x[i, j]() >= 0.9:
            arcs.append((i, j))

path_creation = 0

routes = {v + 1 : [origins[v]] for v in range(len(origins))}

while path_creation < len(origins):
    for i, j in arcs:
        for v in routes:
            if routes[v][-1][-1] == i and routes[v][-1][-1] != 1:
                routes[v].append((i, j))
        for v in routes:
            if routes[v][-1][-1] == 1:
                path_creation += 1
        if path_creation < len(origins):
            path_creation = 0

# Plotting the Solution

colors = ["#"+''.join([random.choice('0123456789ABCDEF') for _ in range(6)]) for _ in range(len(origins))]

vehicle_nodes = {v : [] for v in routes}


for v in vehicle_nodes:
    for i, j in routes[v]:
        if j != model.N.at(1):
            vehicle_nodes[v].append(j)

route_colors = {v : c for v, c in zip(routes, colors)}

node_colors_dict = {model.N.at(1) : "black"}

for v in routes:
    for node in vehicle_nodes[v]:
        node_colors_dict[node] = route_colors[v]

node_colors = []
for loc in model.N:
    node_colors.append(node_colors_dict[loc])
    
city_positions = {}
for node in model.N:
    city_positions[node] = coords[node-1]

G = nx.DiGraph()

G.add_nodes_from(model.N)

for v in routes:
    for c1, c2 in routes[v]:
        G.add_edge(c1, c2, color = route_colors[v])
edge_colors = [G[p1][p2]["color"] for p1, p2 in G.edges()]

edge_labels = {}
for u, v in G.edges:
    edge_labels[(u, v)] = matrix[u-1][v-1]
    
fig, ax = plt.subplots(figsize = (50, 50))
    
nx.draw(G, pos = city_positions, with_labels = True, node_color = node_colors, 
        node_shape = "o", edge_color = edge_colors, arrowstyle = "->", font_color = "white", 
        font_size = 7, node_size = 5, font_weight = "bold")

nx.draw_networkx_nodes(G, pos = city_positions, nodelist = [1], 
                      node_color = "black", label = "Depot")

for v in routes:
    nx.draw_networkx_nodes(G, pos = city_positions, nodelist = vehicle_nodes[v], 
                          node_color = route_colors[v], label = f"Route-{v}")

plt.axis("on")
ax.tick_params(left = "True", bottom = "True", labelleft = "True", labelbottom = "True")
ax.set_xlim([-10, 115])
plt.title("VRPTW")
plt.xticks()
plt.yticks()
plt.xlabel("X-Disance (km)")
plt.ylabel("Y-Disance (km)")
plt.grid()
plt.legend(loc = "best")
plt.show()

        
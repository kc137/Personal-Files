import pyomo.environ as pyo, pandas as pd, networkx as nx, matplotlib.pyplot as plt, math
from pyomo.opt import SolverFactory

# Model

model = pyo.ConcreteModel()

# Required constants

N = 21
V = 5
Vcap = [100 for i in range(V)]

# Required data for Plots

depot_color = "red"
colors = ["darkviolet", "limegreen", "darkorange", "magenta", "darkturquoise"]

# Sets and Parameters

model.N = pyo.Set(initialize = ["D"] + ["L" + str(i) for i in range(1, N)])
model.L = pyo.Set(initialize = ["L" + str(i) for i in range(1, N)])
model.V = pyo.Set(initialize = ["V" + str(i) for i in range(1, V+1)])

model.coords = pd.read_excel("CVRP 20X20.xlsx", sheet_name = "Coords", index_col = 0, header = 0, 
                             usecols = "A:C", nrows = 21)
coords = model.coords

# Calculating Distance

distance = {k : [] for k in model.N}

for p1 in model.N:
    for p2 in model.N:
        if p1 == p2:
            distance[p1].append(0)
        else:
            distance[p1].append(
                round(math.hypot(coords["x"][p1] - coords["x"][p2], 
                                 coords["y"][p1] - coords["y"][p2])))

distance_network = pd.DataFrame(distance, index = model.N)

# Demands

model.demands = pd.read_excel("CVRP 20X20.xlsx", sheet_name = "Demands", index_col = 0, header = 0, 
                             usecols = "A:B", nrows = 21)
demands = model.demands

vehicle_capacity = {model.V.at(i+1) : Vcap[i] for i in range(V)}

model.VC = pyo.Param(model.V, domain = pyo.Any, initialize = vehicle_capacity)

# Variables

model.x = pyo.Var(model.N, model.N, model.V, domain = pyo.Binary)
x = model.x
model.u = pyo.Var(model.N, domain = pyo.NonNegativeReals)
u = model.u

# Constraints

def Once(model, j):
    return sum(x[i, j, k] for k in model.V for i in model.N) == 1
model.once_cons = pyo.Constraint(model.L, rule = Once)

def Flow(model, k, j):
    return (sum(x[i, j, k] for i in model.N if i != j) == 
            sum(x[j, i, k] for i in model.N))
model.flow_cons = pyo.Constraint(model.V, model.L, rule = Flow)

model.depot = pyo.ConstraintList()

for k in model.V:
    model.depot.add(sum(x["D", j, k] for j in model.L) == 1)

model.Subtour = pyo.ConstraintList()

for k in model.V:
    for i in model.L:
        for j in model.L:
            model.Subtour.add(u[j] - u[i] >= demands["Demands"][j] 
                              - model.VC[k]*(1 - x[i, j, k]))

def Capacity(model, k):
    return sum(x[i, j, k]*demands["Demands"][j] for i in model.N
               for j in model.L if i != j) <= model.VC[k]
model.capacity_cons = pyo.Constraint(model.V, rule = Capacity)

# Objective Function

def Obj_Fn(model):
    return sum(x[i, j, k]*distance_network[j][i] 
               for k in model.V
               for i in model.N
               for j in model.N if i != j)
model.Obj = pyo.Objective(rule = Obj_Fn, sense = pyo.minimize)

# Solution

sol = SolverFactory("cplex")
res = sol.solve(model, timelimit = 5)

routes = {v : [] for v in model.V}
tload = 0
for k in model.V:
    vload, vdist = 0, 0
    for i in model.N:
        for j in model.N:
            if x[i, j, k]() and x[i, j, k]() >= 0.9:
                routes[k].append((i, j))
                vload += demands["Demands"][j]
                tload += demands["Demands"][j]
                vdist += distance_network[j][i]
    print(f"\n{routes[k]}")
    print(f"\nVehicle-{k} travelled a distance of {vdist} and delivered a load of {vload}-tons.")
print(f"\nTotal distance travelled by all {V}-vehicles = {model.Obj()} kms and delivered"
      f" a load of {tload}-tons.")

# Setting of Data for Plotting of CVRP

vehicle_colors = {v : c for v, c in zip(model.V, colors)}

edges = routes.copy()
nodes = {v : [] for v in model.V}
for v in model.V:
    for edge in edges[v]:
        if edge[0] != model.N.at(1):
            nodes[v].append(edge[0])

node_colors_dict = {model.N.at(1) : depot_color}
for v in model.V:
    for node in nodes[v]:
        node_colors_dict[node] = vehicle_colors[v]
node_colors = []
for loc in model.N:
    node_colors.append(node_colors_dict[loc])

city_positions = {}
for node in model.N:
    city_positions[node] = (coords["x"][node], coords["y"][node])

# Defining the NetworkX Graph

G = nx.DiGraph()

G.add_nodes_from(model.N)

for veh in edges:
    for p1, p2 in edges[veh]:
        G.add_edge(p1, p2, color = vehicle_colors[veh])
edge_colors = [G[x][y]["color"] for x, y in G.edges()]

# edge_labels = {(u, v) : f"{veh for veh in routes if (u, v) in routes[veh]}-{distance_network[v][u]}" 
#                for u, v in G.edges()}
edge_labels = {}
for veh in routes:
    for u, v in G.edges():
        if (u, v) in routes[veh]:
            edge_labels[(u, v)] = distance_network[v][u]

fig, ax = plt.subplots(figsize = (35, 35))

plt.figure(1)

nx.draw(G, pos = city_positions, with_labels = True, node_size = 1400, node_color = node_colors, 
        node_shape = "o", edge_color = edge_colors, font_size = 17, font_weight = "bold", 
        arrowsize = 20, font_color = "white", width = 4)
for veh in model.V:
    nx.draw_networkx_nodes(G, pos = city_positions, nodelist = nodes[veh], 
                                node_color = vehicle_colors[veh], label = f"Vehicle-{veh}")
nx.draw_networkx_edge_labels(G, pos = city_positions, edge_labels = edge_labels, 
                             label_pos = 0.45, font_size = 20)

plt.axis("on")
ax.tick_params(left = True, bottom = True, labelleft = "True", labelbottom = "True")
plt.title("CVRP for 20 CIties", fontsize = 25)
plt.xticks(fontsize = 20)
plt.yticks(fontsize = 20)
plt.xlabel("X-Distance (km)", fontsize = 25)
plt.ylabel("Y-Distance (km)", fontsize = 25)
plt.grid(linewidth = 3)
plt.legend(fontsize = 25, loc = "best")
plt.show()









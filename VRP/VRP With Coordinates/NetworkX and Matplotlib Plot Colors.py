import networkx as nx
import pyomo.environ as pyo, pandas as pd, matplotlib.pyplot as plt, math
from pyomo.opt import SolverFactory
from collections import defaultdict

# Model

model = pyo.ConcreteModel()

N = 16
V = 4
Vcap = [100, 100, 100, 100]


# Sets

model.N = pyo.Set(initialize = ["D"] + ["C" + str(i) for i in range(1, N)])
model.C = pyo.Set(initialize = ["C" + str(i) for i in range(1, N)])
model.V = pyo.Set(initialize = ["V" + str(i) for i in range(1, V+1)])

# Params

model.coords = pd.read_excel("CVRP_16_16.xlsx", sheet_name = "Coords", index_col = 0, header = 0, nrows = 16, usecols = "A:C")
coords = model.coords

distance = {k : [] for k in model.N}
for P1 in model.N:
    for P2 in model.N:
        if P1 == P2:
            distance[P1].append(0)
        else:
            distance[P1].append(round(math.hypot(
                (coords["x"][P1] - coords["x"][P2]), (coords["y"][P1] - coords["y"][P2]))))
            
distance_network = pd.DataFrame(distance, index = model.N)

# Plots

colors = ["violet", "limegreen", "darkorange", "gold", "blue"]
vehicle_colors = {v : c for v, c in zip(model.V, colors)}

G = nx.Graph()

rout = [[('D', 'C1'), ('C1', 'C6'), ('C5', 'D'), ('C6', 'C13'), ('C13', 'C5')], 
        [('D', 'C14'), ('C3', 'C8'), ('C4', 'D'), ('C8', 'C4'), ('C14', 'C3')], 
        [('D', 'C7'), ('C2', 'D'), ('C7', 'C15'), ('C9', 'C2'), ('C15', 'C9')], 
        [('D', 'C10'), ('C10', 'C11'), ('C11', 'C12'), ('C12', 'D')]]

edges = {v : paths for v, paths in zip(model.V, rout)}

nodes = {k : [] for k in model.V}
for veh in edges:
    for path in edges[veh]:
        if path[0] != "D":
            nodes[veh].append(path[0])

node_colors_dict = {"D" : "red"}
for veh in model.V:
    for node in nodes[veh]:
        node_colors_dict[node] = vehicle_colors[veh]

node_colors = ["red"]
for node in model.N:
    if node != "D":
        node_colors.append(node_colors_dict[node])

city_positions = {}
for city in model.N:
    city_positions[city] = (coords["x"][city], coords["y"][city])

# # for i in range(len(nodes)):
# #     G.add_node(nodes[i])
G.add_nodes_from(model.N)

for veh in edges:
    for p1, p2 in edges[veh]:
        G.add_edge(p1, p2, color = vehicle_colors[veh])
edge_colors = [G[x][y]["color"] for x, y in G.edges()]

edge_labels = {(u, v) : distance_network[v][u] for u, v in G.edges()}

fig, ax = plt.subplots(figsize=(45, 35))

plt.figure(1)

# nx.draw(G, with_labels = True, node_size = 1000, node_color = node_colors, node_shape = "o", pos = city_positions, 
#         edge_color = edge_colors, font_size = 15, font_weight = "bold", font_color = "white", width = 2)
# nx.draw_networkx_edge_labels(G, pos = city_positions, edge_labels = edge_labels)

nx.draw(G, pos = city_positions, with_labels = True, node_size = 1500, node_color = node_colors, node_shape = "o", 
        edge_color = edge_colors, font_size = 20, font_weight = "bold", font_color = "white", width = 4)
nx.draw_networkx_edge_labels(G, pos = city_positions, edge_labels = edge_labels, font_size = 17)

# bbox=dict(facecolor="green", edgecolor='black', boxstyle='round,pad=0.02')
# ax.set_xlim(0, 6)
# ax.set_ylim(0, 6)

plt.axis("on")
ax.tick_params(left = True, bottom = True, labelleft = True, labelbottom = True)
plt.title("VRP of 16 CIties", fontsize=25)
plt.xticks(fontsize = 20)
plt.yticks(fontsize = 20)
plt.xlabel("X-Distance", fontsize=25)
plt.ylabel("Y-Distance", fontsize=25)
plt.grid(linewidth = 2.5)
plt.legend(vehicle_colors)
plt.show()

# nx.draw(G, with_labels = True, pos = city_positions, node_color = node_colors, 
#         edge_color = edge_colors, width = 2)

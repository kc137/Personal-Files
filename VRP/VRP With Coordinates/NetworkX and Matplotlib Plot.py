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
N = 16

G = nx.Graph()

nodes = ["D"] + ["C" + str(i) for i in range(1, N)]
rout = [('D', 'C1'), ('C1', 'C6'), ('C5', 'D'), ('C6', 'C13'), ('C13', 'C5'), 
        ('D', 'C14'), ('C3', 'C8'), ('C4', 'D'), ('C8', 'C4'), ('C14', 'C3'), 
        ('D', 'C7'), ('C2', 'D'), ('C7', 'C15'), ('C9', 'C2'), ('C15', 'C9'), 
        ('D', 'C10'), ('C10', 'C11'), ('C11', 'C12'), ('C12', 'D')]
colors = ["red"] + ["green" for _ in range(1, 16)]

city_positions = {}
for city in model.N:
    city_positions[city] = (coords["x"][city], coords["y"][city])

# for i in range(len(nodes)):
#     G.add_node(nodes[i])
G.add_nodes_from(nodes)
G.add_edges_from(rout)

fig, ax = plt.subplots(figsize=(20, 20))

plt.figure(1)

nx.draw(G, with_labels = True, node_size = 2500, node_color = colors, node_shape = "o", pos = city_positions, 
        font_size = 20, font_weight = "bold", font_color = "yellow", width = 2)
# bbox=dict(facecolor="green", edgecolor='black', boxstyle='round,pad=0.02')
# ax.set_xlim(0, 6)
# ax.set_ylim(0, 6)
plt.axis("on")
ax.tick_params(left = True, bottom = True, labelleft = True, labelbottom = True)
plt.show()
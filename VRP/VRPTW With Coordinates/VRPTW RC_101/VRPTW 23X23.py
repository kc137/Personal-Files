import pyomo.environ as pyo, pyomo.gdp as dp, pandas as pd, math, numpy as np
import matplotlib.pyplot as plt, networkx as nx
from pyomo.opt import SolverFactory

# Model

model = pyo.ConcreteModel()

# Required Constants

N = 23
V = 5
Vcap = [100 for _ in range(V)]
Pen = 100
BigM = 1000

# Required data for plots

depot_color = "red"
colors = ["darkviolet", "limegreen", "darkorange", "magenta", "darkturquoise"]

# Sets and Parameters

model.N = pyo.Set(initialize = ["D"] + ["C" + str(i) for i in range(1, N)])
model.C = pyo.Set(initialize = ["C" + str(i) for i in range(1, N)])
model.V = pyo.Set(initialize = ["V" + str(i) for i in range(1, V+1)])

model.inputs = pd.read_excel("VRPTW 23X23.xlsx", sheet_name = "Data", index_col = 0, header = 0, 
                             usecols = "A:G", nrows = 23)
data = model.inputs

# Distance Calculation

distance = {k : [] for k in model.N}
for p1 in model.N:
    for p2 in model.N:
        if p1 != p2:
            distance[p1].append(round(
                math.hypot((data["YC"][p2] - data["YC"][p1]), (data["XC"][p2] - data["XC"][p1]))))
        else:
            distance[p1].append(0)

distance_network = pd.DataFrame(distance, index = model.N)

# distance_network.to_excel("Network_23X23.xlsx", sheet_name = "Network")

vehicle_capacity = {model.V.at(i+1) : Vcap[i] for i in range(V)}

model.VC = pyo.Param(model.V, domain = pyo.Any, initialize = vehicle_capacity)

# Variables

# Decision Binary Variables
model.x = pyo.Var(model.N, model.N, model.V, domain = pyo.Binary)
x = model.x
# Times
model.s = pyo.Var(model.N, model.V, domain = pyo.NonNegativeReals, bounds = (0, 300))
s = model.s
# Lower Bound Violation
model.lbv = pyo.Var(model.N, domain = pyo.NonNegativeReals, bounds = (0, 300))
lbv = model.lbv
# Upper Bound Violation
model.ubv = pyo.Var(model.N, domain = pyo.NonNegativeReals, bounds = (0, 300))
ubv = model.ubv

# Constraints

def Once(model, j):
    return sum(x[i, j, k] for i in model.N for k in model.V) == 1
model.once_cons = pyo.Constraint(model.C, rule = Once)

def Flow(model, k, j):
    return (sum(x[i, j, k] for i in model.N if i != j) == 
            sum(x[j, i, k] for i in model.N))
model.flow_cons = pyo.Constraint(model.V, model.C, rule = Flow)

model.depot = pyo.ConstraintList()

for k in model.V:
    model.depot.add(sum(x["D", j, k] for j in model.C) == 1)
    
model.times = pyo.ConstraintList() # Cover the subtours

# Capacity Constraints

def Capacity(model, k):
    return sum(x[i, j, k]*data["DEMAND"][j] for i in model.N 
               for j in model.C if i != j) <= model.VC[k]
model.capacity_cons = pyo.Constraint(model.V, rule = Capacity)

model.Time_Cons = pyo.ConstraintList()

for k in model.V:
    model.Time_Cons.add(s["D", k] == 0)

for k in model.V:
    for i in model.C:
        for j in model.C:
            if i != j:
                model.Time_Cons.add(s[i, k] + distance_network[j][i] + 
                                    data["SERVICE_TIME"][j] 
                                    <= BigM*(1 - x[i, j, k]) + s[j, k] - 0.00001)
    
# Now we define Disjunctions for time violations

def disj_lbv1(model, j, k):
    d1 = dp.Disjunct()
    d1.C1 = pyo.Constraint(expr = s[j, k] >= data["START_TIME"][j])
    d1.C2 = pyo.Constraint(expr = lbv[j] == 0)
    model.add_component(f"d1_{j}_{k}", d1)
    return d1

def disj_lbv2(model, j, k):
    d2 = dp.Disjunct()
    d2.C1 = pyo.Constraint(expr = s[j, k] <= data["START_TIME"][j])
    d2.C2 = pyo.Constraint(expr = lbv[j] == data["START_TIME"][j] - s[j, k])
    model.add_component(f"d2_{j}_{k}", d2)
    return d2

def disj_lbv(model, j, k):
    fst = disj_lbv1(model, j, k)
    snd = disj_lbv2(model, j, k)
    return [fst, snd]

model.disj_lbv_cons = dp.Disjunction(model.N, model.V, rule = disj_lbv)
    
def disj_ubv1(model, j, k):
    d3 = dp.Disjunct()
    d3.C1 = pyo.Constraint(expr = s[j, k] + data["SERVICE_TIME"][j] <= data["DUE_TIME"][j])
    d3.C2 = pyo.Constraint(expr = ubv[j] == 0)
    model.add_component(f"d3_{j}_{k}", d3)
    return d3

def disj_ubv2(model, j, k):
    d4 = dp.Disjunct()
    d4.C1 = pyo.Constraint(expr = s[j, k] + data["SERVICE_TIME"][j] >= data["DUE_TIME"][j])
    d4.C2 = pyo.Constraint(expr = ubv[j] == s[j, k] + data["SERVICE_TIME"][j] - data["DUE_TIME"][j])
    model.add_component(f"d4_{j}_{k}", d4)
    return d4

def disj_ubv(model, j, k):
    fst = disj_ubv1(model, j, k)
    snd = disj_ubv2(model, j, k)
    return [fst, snd]

model.disj_ubv_cons = dp.Disjunction(model.N, model.V, rule = disj_ubv)

pyo.TransformationFactory("gdp.hull").apply_to(model)

# Objective Function

min_distance = sum(x[i, j, k]*distance_network[j][i] 
                   for k in model.V 
                   for i in model.N 
                   for j in model.N if i != j)
min_lbv = sum(lbv[i] for i in model.N)
min_ubv = sum(ubv[i] for i in model.N)

def Obj_Fn(model):
    return min_distance + min_lbv + min_ubv
model.Obj = pyo.Objective(rule = Obj_Fn, sense = pyo.minimize)

# Solution

sol = SolverFactory("cplex")
# sol.options["mipgap"] = 0.6
# sol.options["tee"] = True
res = sol.solve(model, tee = False, timelimit = 15)

routes = {k : [] for k in model.V}
sol_time_windows = {k : [] for k in model.V}
tload = 0
for k in model.V:
    vload, vdist = 0, 0
    for i in model.N:
        for j in model.N:
            if x[i, j, k]() and round(x[i, j, k]()) == 1:
                routes[k].append((i, j))
                vdist += distance_network[j][i]
                vload += data["DEMAND"][j]
                tload += data["DEMAND"][j]
                sol_time_windows[k].append(f"{s[j, k]} = {round(s[j, k]()) + data['SERVICE_TIME'][j]} - ({data['START_TIME'][j]}, {data['DUE_TIME'][j]})")
    print(routes[k])
    print(f"\nVehicle travelled {vdist} km with a load of {vload} Tons.")

print(f"\nTotal distance travelled = {min_distance()}")

# Plotting the Solution

# vehicle_colors = {model.V.at(i+1) : colors[i] for i in range(V)}
vehicle_colors = {v : c for v, c in zip(model.V, colors)}

edges = routes.copy()

nodes = {v : [] for v in model.V}
for v in model.V:
    for path in edges[v]:
        if path[0] != model.N.at(1):
            nodes[v].append(path[0])

node_colors_dict = {model.N.at(1) : depot_color}
for v in model.V:
    for node in nodes[v]:
        node_colors_dict[node] = vehicle_colors[v]
node_colors = []
for node in model.N:
    node_colors.append(node_colors_dict[node])

city_positions = {}
for loc in model.N:
    city_positions[loc] = (data["XC"][loc], data["YC"][loc])
    
# Defining the NetworkX Graph

G = nx.DiGraph()

G.add_nodes_from(model.N)

for veh in edges:
    for p1, p2 in edges[veh]:
        G.add_edge(p1, p2, color = vehicle_colors[veh])
edge_colors = [G[x][y]["color"] for x, y in G.edges()]

edge_labels = {}
for u, v in G.edges:
    edge_labels[(u, v)] = distance_network[v][u]

fig, ax = plt.subplots(figsize = (35, 35))
plt.figure(1)

nx.draw(G, pos = city_positions, with_labels = True, node_size = 1400, node_color = node_colors, 
        node_shape = "o", edge_color = edge_colors, font_size = 17, font_weight = "bold", 
        arrowsize = 20, arrowstyle = "->", font_color = "white", width = 4)

for veh in model.V:
    nx.draw_networkx_nodes(G, pos = city_positions, nodelist = nodes[veh], 
                           node_color = vehicle_colors[veh], label = f"Vehicle-{veh}")
nx.draw_networkx_edge_labels(G, pos = city_positions, edge_labels = edge_labels, 
                             label_pos = 0.5, font_size = 20)

plt.axis("on")
ax.tick_params(left = "True", bottom = "True", labelleft = "True", labelbottom = "True")
plt.title("VRPTW 22 Cities")
plt.xticks(fontsize = 20)
plt.yticks()
plt.xlabel("X-Distance (km)", fontsize = 25)
plt.ylabel("Y-Distance (km)", fontsize = 25)
plt.grid(linewidth = 3)
plt.legend(fontsize = 25, loc = "best")
plt.show()


















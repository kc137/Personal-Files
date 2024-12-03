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

# Eucl_Distance
distance = {k : [] for k in model.N}
for P1 in model.N:
    for P2 in model.N:
        if P1 == P2:
            distance[P1].append(0)
        else:
            distance[P1].append(round(math.hypot(
                (coords["x"][P1] - coords["x"][P2]), (coords["y"][P1] - coords["y"][P2]))))
            
distance_network = pd.DataFrame(distance, index = model.N)

model.demand = pd.read_excel("CVRP_16_16.xlsx", sheet_name = "Demand", index_col = 0, header = 0, nrows = 16, usecols = "A:B")
demand = model.demand

# xy_coords = []

# for i, j in zip(coords["x"], coords["y"]):
#     xy_coords.append((i, j))
# xc, yc = zip(*xy_coords)
# scplot = plt.scatter(xc, yc)

routes = {}

rout = [[('D', 'C1'), ('C1', 'C6'), ('C5', 'D'), ('C6', 'C13'), ('C13', 'C5')], 
        [('D', 'C14'), ('C3', 'C8'), ('C4', 'D'), ('C8', 'C4'), ('C14', 'C3')], 
        [('D', 'C7'), ('C2', 'D'), ('C7', 'C15'), ('C9', 'C2'), ('C15', 'C9')], 
        [('D', 'C10'), ('C10', 'C11'), ('C11', 'C12'), ('C12', 'D')]]

for v in range(len(model.V)):
    routes[model.V.at(v+1)] = (rout[v])

vehi_points = {k : ["D"] for k in model.V}
for k in routes:
    visit = set()
    visit.add(routes[k][0])
    vehi_points[k].append(routes[k][0][1])
    while len(visit) < len(routes[k]):
        for tup in routes[k]:
            if tup[0] == vehi_points[k][-1]:
                visit.add(tup)
                vehi_points[k].append(tup[1])

route_coord = {k : [] for k in model.V}

for route in vehi_points:
    for p in vehi_points[route]:
        route_coord[route].append((coords["x"][p], coords["y"][p]))

for v in route_coord:
    path = route_coord[v]
    xp, yp = zip(*path)
    plt.scatter(xp, yp)
    plt.plot(xp, yp)





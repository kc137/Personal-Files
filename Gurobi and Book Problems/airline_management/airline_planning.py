import pyomo.environ as pyo, pandas as pd, networkx as nx, matplotlib.pyplot as plt, matplotlib
from datetime import datetime, timedelta
from pyomo.opt import SolverFactory
import warnings
warnings.filterwarnings("ignore")
matplotlib.use("tkagg")

df_plan = pd.read_csv("flight_rotations_2006-07-01.csv")
# df_plan['start_time'] = pd.to_datetime(df_plan['start_time'], format='%H:%M')
# df_plan['start_time'] = df_plan['start_time'].dt.time
# df_plan['end_time'] = pd.to_datetime(df_plan['end_time'], format='%H:%M')
# df_plan['end_time'] = df_plan['end_time'].dt.time
# df_plan['duration'] = pd.to_datetime(df_plan['duration'], format='%H:%M')
# df_plan['duration'] = df_plan['duration'].dt.time
# print(df_plan.head())

# flights = df_plan.flight.unique()
# aircrafts = df_plan.aircraft.unique()
# airports = set(df_plan.ori.unique() + df_plan.des.unique())


from IPython.display import Image, display
import networkx as nx
from networkx.drawing.nx_agraph import graphviz_layout
from networkx.drawing.nx_agraph import to_agraph

arcs = list(df_plan[["ori","des"]].itertuples(index = False, name = None))
n_airports = 4

G = nx.MultiDiGraph()
G.add_edges_from(arcs)

top_airports = [i for (i,j) in sorted(G.degree, key=lambda x: x[1], reverse=True)[:n_airports]] # pre-select top airports by their degree

G = G.subgraph(top_airports) # reduce the graph to just the top few airports

df_plan = df_plan[df_plan["ori"].isin(top_airports)]
df_plan = df_plan[df_plan["des"].isin(top_airports)]

df_plan['start_time'] = pd.to_datetime(df_plan['start_time'], format='%H:%M')
df_plan['start_time'] = df_plan['start_time'].dt.time
df_plan['end_time'] = pd.to_datetime(df_plan['end_time'], format='%H:%M')
df_plan['end_time'] = df_plan['end_time'].dt.time
df_plan['duration'] = pd.to_datetime(df_plan['duration'], format='%H:%M')
df_plan['duration'] = df_plan['duration'].dt.time

flights = df_plan.flight.unique()
aircrafts = df_plan.aircraft.unique()
airports = set(df_plan.ori.unique() + df_plan.des.unique())

flight_origin = df_plan.set_index("flight").ori.to_dict()
flight_dest = df_plan.set_index("flight").des.to_dict()
flight_start = df_plan.set_index("flight").start_time.to_dict()
flight_end = df_plan.set_index("flight").end_time.to_dict()

df_start = pd.read_csv("starting_positions.csv")
# print(df_start.head())
aircrafts_start_pos = df_start.set_index("aircraft").airport.to_dict()

df_end = pd.read_csv("ending_positions.csv")
aircrafts_end_pos = df_end.set_index("aircraft").airport.to_dict()

df_itineraries = pd.read_csv("flight_iterinaries.csv")
df_itineraries["total_cost"] = df_itineraries.cost*df_itineraries.n_pass
# flight_revenue = df_itineraries.groupby(["flight"])["total_cost"].agg("sum").to_dict()
flight_revenue = df_itineraries.groupby(["flight"])["total_cost"].agg("sum").to_dict()
flight_n_pass = df_itineraries.groupby(["flight"])["n_pass"].agg("sum").to_dict()

# print(df_itineraries.head())

# aircraft_flights = df_plan.groupby(['aircraft'], ).apply(lambda x: x['flight'].tolist(), include_groups = False).to_dict()

# print(flight_revenue.tail(20))

from ipywidgets import interact, interactive, fixed, interact_manual

aircraft_flights = df_plan.groupby(['aircraft']).apply(lambda x: x['flight'].tolist()).to_dict()

flight_arcs_for_each_aircraft = {}
deltaplus_flightarcs = {}
deltaminus_flightarcs = {}
for a in aircraft_flights:
    aircraft_flights[a] += [f"source_{a}",f"sink_{a}"]
    flight_origin[f"source_{a}"] = aircrafts_start_pos[a]
    flight_dest[f"source_{a}"] = aircrafts_end_pos[a]
    flight_origin[f"sink_{a}"] = aircrafts_end_pos[a]
    flight_dest[f"sink_{a}"] = aircrafts_start_pos[a]

    flight_start[f"source_{a}"] = datetime.strptime('0:0', '%H:%M').time()
    flight_end[f"source_{a}"] = datetime.strptime('0:0', '%H:%M').time()

    flight_start[f"sink_{a}"] = datetime.strptime('23:59', '%H:%M').time()
    flight_end[f"sink_{a}"] = datetime.strptime('23:59', '%H:%M').time()

    flight_arcs_for_each_aircraft[a] = []
    deltaplus_flightarcs[a] = {f: [] for f in aircraft_flights[a]}
    deltaminus_flightarcs[a] = {f: [] for f in aircraft_flights[a]}

    for f1 in aircraft_flights[a]:
        for f2 in aircraft_flights[a]:
            if f1!=f2 and flight_end[f1] < flight_start[f2] and flight_dest[f1] == flight_origin[f2]:
                flight_arcs_for_each_aircraft[a].append((f1,f2))
                deltaplus_flightarcs[a][f1].append(f2)
                deltaminus_flightarcs[a][f2].append(f1) 

set_flights = set()
for ac in aircraft_flights:
    for fl in aircraft_flights[ac]:
        set_flights.add(fl)
# print(len(set_flights))
pyomo_flights = list(set_flights)

N = ('LYS', 'NCE', 'ORY', 'CDG')

# Pyomo Model

model = pyo.ConcreteModel()

# Sets and Parameters

model.A = pyo.Set(initialize = aircrafts)
model.F = pyo.Set(initialize = pyomo_flights)

"""
Fa, Ea, rf, (of, df), (Ciarr, Cidep)
"""

x_idx = []
y_idx = []
for a in aircrafts:
    for f in aircraft_flights[a]:
        x_idx.append((a, f))
        
    for (f1,f2) in flight_arcs_for_each_aircraft[a]:
        y_idx.append((a, f1, f2))
# print(vars)

# Variables

model.x = pyo.Var(x_idx, within = pyo.Binary)
x = model.x

model.y = pyo.Var(y_idx, within = pyo.Binary)
y = model.y

# Constraints

# Cons-1

model.st_in_end = pyo.ConstraintList()

for a in aircrafts:
    model.st_in_end.add(
        pyo.quicksum(y[a, f"source_{a}", f2] for f2 in deltaplus_flightarcs[a][f"source_{a}"]) == 1
        )
    model.st_in_end.add(
        pyo.quicksum(y[a, f1, f"sink_{a}"] for f1 in deltaminus_flightarcs[a][f"sink_{a}"]) == 1
        )
    for f in aircraft_flights[a]:
        if str(f)[0] != "s":
            try:
                model.st_in_end.add(
                    pyo.quicksum(y[a, f, f2] for f2 in deltaplus_flightarcs[a][f]) == \
                      pyo.quicksum(y[a, f1, f] for f1 in deltaminus_flightarcs[a][f])
                    )
            except ValueError:
                pass

# Cons-2

model.operation = pyo.ConstraintList()

for a in aircrafts:
    for f in aircraft_flights[a]:
        model.operation.add(
            x[a, f] <= pyo.quicksum(y[a, f, f2] for f2 in deltaplus_flightarcs[a][f])
            )

# Cons-3

alpha = 0.5

model.max_limit = pyo.ConstraintList()
for i in N:
    total_dep = len([f for a in aircrafts 
                    for f in aircraft_flights[a] 
                    if flight_origin[f] == i])
    total_arri = len([f for a in aircrafts 
                     for f in aircraft_flights[a] 
                     if flight_dest[f] == i])
    model.max_limit.add(
        pyo.quicksum(x[a, f] for a in aircrafts for f in aircraft_flights[a] 
                     if flight_origin[f] == i) <= alpha*total_dep
        )
    model.max_limit.add(
        pyo.quicksum(x[a, f] for a in aircrafts for f in aircraft_flights[a] 
                     if flight_dest[f] == i) <= alpha*total_arri
        )

# Objective Function

def obj_fn(model):
    return pyo.quicksum((1 - x[a, f])*flight_revenue[f] 
                        for a in aircrafts 
                        for f in aircraft_flights[a] 
                        if f in flight_revenue)
model.obj = pyo.Objective(rule = obj_fn, sense = pyo.minimize)

# Solution

sol = SolverFactory("cplex")
res = sol.solve(model)

# Printing the Solution

operated_flights = {a: [f for f in aircraft_flights[a] if x[a,f]() > .5 if str(f)[0] != 's'] for a in aircrafts}

print(f"The total profit after disruptions of flights for the Company : {model.obj()} $.")

print(f"Optimal Flights served : {sum(len(operated_flights[a]) for a in aircrafts)}")

print(f"Optimal number of passengers transported : {sum(sum(flight_n_pass[f] for f in aircraft_flights[a] if x[a,f]() > .5) for a in aircrafts)}")

print(f"Optimal aircrafts utilized : {sum([1 if len(operated_flights[a]) > 0 else 0 for a in aircrafts])}")

# with open("origin.txt", "w") as origin:
#     for k, v in flight_revenue:
#         origin.write(f"[{k} - Val-{v}]\n")

















# # visualize the network
# A_graph = to_agraph(G) 
# A_graph.layout('dot')    
# display(A_graph)

# def visualize_aircraft_network(x): 
#     G = nx.DiGraph()
#     G.add_edges_from(flight_arcs_for_each_aircraft[x])
#     plt.figure(figsize=(20,14)) 
#     A_graph = to_agraph(G) 
#     A_graph.layout('dot')    
#     display(A_graph)             
#     plt.show()
 
# interact(visualize_aircraft_network, x=aircraft_flights.keys())
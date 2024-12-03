import networkx as nx
from vrpy import VehicleRoutingProblem

# Create graph
G = nx.DiGraph()
for v in [1, 2, 3, 4, 5]:
    G.add_edge("Source", v, cost=10, time=20)
    G.add_edge(v, "Sink", cost=10, time=20)
    G.nodes[v]["demand"] = 5
    G.nodes[v]["upper"] = 100
    G.nodes[v]["lower"] = 5
    G.nodes[v]["service_time"] = 1
G.nodes[2]["upper"] = 20
G.nodes["Sink"]["upper"] = 110
G.nodes["Source"]["upper"] = 100
G.add_edge(1, 2, cost=10, time=20)
G.add_edge(2, 3, cost=10, time=20)
G.add_edge(3, 4, cost=15, time=20)
G.add_edge(4, 5, cost=10, time=25)

# Create vrp
prob = VehicleRoutingProblem(G, num_stops=3, load_capacity=10, duration=64, time_windows=True)

# Solve and display solution
prob.solve()
print(prob.best_routes)
print(prob.best_value)

nx.draw(G)
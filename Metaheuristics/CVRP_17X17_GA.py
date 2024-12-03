import math, random, pandas as pd, networkx as nx, matplotlib.pyplot as plt, time, numpy as np, matplotlib
matplotlib.use("tkagg")

from numpy.random import randint
from deap import base, creator, tools, algorithms, benchmarks

# Time Start

start = time.time()

# Colors

colors = ["darkviolet", "limegreen", "darkorange", "magenta", "darkturquoise"]

# Customers

coords_list = [(40, 50),
 (25, 85),
 (22, 75),
 (22, 85),
 (20, 80),
 (20, 85),
 (18, 75),
 (15, 75),
 (15, 80),
 (10, 35),
 (10, 40),
 (8, 40),
 (8, 45),
 (5, 35),
 (5, 45),
 (2, 40),
 (0, 40),
 (0, 45),
 (44, 5),
 (42, 10),
 (42, 15),
 (40, 5),
 (40, 15),
 (38, 5),
 (38, 15),
 (35, 5)]

N = len(coords_list) - 1

# distances = {n : [] for n in range(N+1)}

distance_network = np.zeros([N+1, N+1], dtype = int)

for n1 in range(N+1):
    for n2 in range(N+1):
        if n1 != n2:
            distance_network[n1][n2] = \
                round(math.hypot(coords_list[n1][0] - coords_list[n2][0], 
                           coords_list[n1][1] - coords_list[n2][1]))
        else:
            distance_network[n1][n2] = 0

# distance_network = pd.DataFrame(distances)

initial_flow = [n for n in range(1, N+1)]
random.shuffle(initial_flow)

# demands = [0, 15, 25, 34, 25, 20, 28, 17, 33, 25, 22, 19, 27, 20, 16, 21, 20]

# demands = pd.DataFrame(demands, index = [n for n in range(N+1)], columns = ["C"])

demands = np.array([0, 15, 25, 34, 25, 20, 28, 17, 33, 25, 22, 19, 27, 20, 16, 21, 20])

capacity = 100
    
def get_fitness(genes):
    fitness = 0
    prev = 0
    cumu_demand = 0
    
    for loc in genes:
        if cumu_demand + demands[loc] <= capacity:
            cumu_demand += demands[loc]
            fitness += distance_network[loc][prev]
            prev = loc
        else:
            fitness += distance_network[0][prev]
            cumu_demand = demands[loc]
            prev = 0
            fitness += distance_network[loc][prev]
            prev = loc
    fitness += distance_network[0][genes[-1]]
    return (fitness, )

def get_route_len(individual):
    cumu_demand = 0
    count = 0
    sub_route = []
    
    for loc in individual:
        if cumu_demand + demands[loc] <= capacity:
            cumu_demand += demands[loc]
            count += 1
        else:
            cumu_demand = demands[loc]
            sub_route.append(count)
            count = 1
    sub_route.append(count)
    return sub_route
        
def get_edges(individual, sub_route):

    edges = {i+1 : [] for i in range(len(sub_route))}
    
    i = 0
    for p in range(len(sub_route)):
        for j in range(sub_route[p]):
            if j == 0:
                edges[p+1].append(("D", individual[i]))
                i += 1
            else:
                edges[p+1].append((individual[i-1], individual[i]))
                i += 1
        edges[p+1].append((individual[i-1], "D"))
    return edges
        
def Crossover(parent1, parent2):
    N1, N2 = N-1, N-1
    a = random.randint(2, N1-3)
    b = random.randint(2, N2-3)
    if a == b:
        while a == b:
            b = random.randint(2, N2-3)
    if a > b:
        a, b = b, a
    offspring1 = [0]*N1
    offspring2 = [0]*N2
    
    offspring1[a:b+1] = parent2[a:b+1]
    visit = set(parent2[a:b+1])
    
    j = b+1
    for i in range(N):
        if parent1[(i+b+1) % N1] not in visit:
            offspring1[j] = parent1[(i+b+1) % N1]
            j = (j+1) % N2
            visit.add(parent1[(i+b+1) % N1])
    
    offspring2[a:b+1] = parent1[a:b+1]
    
    visit = set(parent1[a:b+1])
    
    j = b+1
    for i in range(N):
        if parent2[(i+b+1) % N2] not in visit:
            offspring2[j] = parent2[(i+b+1) % N2]
            j = (j+1) % N2
            visit.add(parent2[(i+b+1) % N2])
            
    return offspring1, offspring2

def Mutation(individual, mut_prob):
    for i in range(N):
        if random.random() <= mut_prob:
            swap_idx = random.randint(0, N - 2)
            if swap_idx >= i:
                swap_idx += 1
            individual[i], individual[swap_idx] = individual[swap_idx], individual[i]
    return individual, 
    
class Genetic_Algorithm:
    
    def __init__(self, population_size = 200, crossover_rate = 0.8, mutation_rate = 0.15, num_gens = 150):
        self.population_size = population_size
        self.crossover_rate = crossover_rate
        self.mutation_rate = mutation_rate
        self.num_gens = num_gens
        self.best_solution = []
        self.toolbox = base.Toolbox()
        self.create_creators()
        
    def create_creators(self):
        creator.create("min_fitness", base.Fitness, weights = (-1, ))
        creator.create("Individual", list, fitness = creator.min_fitness)
        
        # Registering Toolbox
        self.toolbox.register("indexes", random.sample, range(1, N+1), N)
        
        # Creating Individual and Population from each Individual
        self.toolbox.register("individual", tools.initIterate, creator.Individual, self.toolbox.indexes)
        self.toolbox.register("population", tools.initRepeat, list, self.toolbox.individual)
        
        # Adding Fitness evaluation function in tools
        self.toolbox.register("eval_fitness", get_fitness)
        
        # Selection Method
        self.toolbox.register("selection", tools.selNSGA2)
        
        # CrossOver Method
        self.toolbox.register("crossover", Crossover)
        
        # Mutation Method
        self.toolbox.register("mutation", Mutation, mut_prob = self.mutation_rate)
    
    def popu_fitness(self):
        self.popu = self.toolbox.population(n = self.population_size)
        self.remaining_indi = [indi for indi in self.popu if not indi.fitness.valid]
        self.fitnesses = list(map(self.toolbox.eval_fitness, self.remaining_indi))
        
        for indi, fitness_value in zip(self.popu, self.fitnesses):
            indi.fitness.values = fitness_value
        
        self.popu = self.toolbox.selection(self.popu, self.population_size)
    
    def run_generations(self):
        generations = 0
                
        while generations != self.num_gens:
            generations += 1
            self.offspring = tools.selTournamentDCD(self.popu, self.population_size)
            self.offspring = [self.toolbox.clone(indi) for indi in self.offspring]
            
            # Now time for performing Crossover and Mutation according to their 
            for indi1, indi2 in zip(self.offspring[::2], self.offspring[1::2]):
                if random.random() <= self.crossover_rate:
                    self.toolbox.crossover(indi1, indi2)
                
                    del indi1.fitness.values, indi2.fitness.values
                
                self.toolbox.mutation(indi1)
                self.toolbox.mutation(indi2)
            
            self.invalid_indivs = [indi for indi in self.offspring if not indi.fitness.values]
            self.fitnesses = self.toolbox.map(self.toolbox.eval_fitness, self.invalid_indivs)
            
            for indi, indi_fitness in zip(self.invalid_indivs, self.fitnesses):
                indi.fitness.values = indi_fitness
                
            self.popu = self.toolbox.selection(self.popu + self.offspring, self.population_size)
            
            best_individual = tools.selBest(self.popu, 1)[0]
            best_distance = best_individual.fitness.values[0]
            
            if generations % 10 == 0:
                print(f"Generation no. : {generations}."
                      f"\nBest path found : {best_individual}."
                      f"\nDistance : {best_distance} m.")
        self.best_solution = best_individual.copy()
    
    def get_best_sol(self):
        return self.best_solution


GA = Genetic_Algorithm(200, 0.85, 0.1, 100)
GA.create_creators()
GA.popu_fitness()
GA.run_generations()                

best_solution = GA.get_best_sol()

end = time.time()

print(f"GA took {round(end - start, 3)} s to find the optimal solution.")

sub_route = get_route_len(best_solution)

# Vehicles

V = len(sub_route)

edges = get_edges(best_solution, sub_route)

vehicle_colors = {v : c for v, c in zip(range(1, V+1), colors)}

nodes = {v : [] for v in range(1, V+1)}

for v in range(1, V+1):
    for edge in edges[v]:
        if edge[0] != "D":
            nodes[v].append(edge[0])

node_colors_dict = {"D" : "red"}
for v in range(1, V+1):
    for node in nodes[v]:
        node_colors_dict[node] = vehicle_colors[v]
node_colors = ["red"]
for loc in range(1, N+1):
    node_colors.append(node_colors_dict[loc])

city_positions = {"D" : coords_list[0]}
for loc in range(1, N+1):
    city_positions[loc] = coords_list[loc]

# Defining NetworkX Graph

G = nx.DiGraph()

G.add_nodes_from(["D"] + best_solution)

for veh in edges:
    for p1, p2 in edges[veh]:
        G.add_edge(p1, p2, color = vehicle_colors[veh])
edge_colors = [G[x][y]["color"] for x, y in G.edges()]

edge_labels = {}
for veh in edges:
    for u, v in G.edges():
        if u == "D":
            edge_labels[(u, v)] = distance_network[0][v]
        elif v == "D":
            edge_labels[(u, v)] = distance_network[u][0]
        else:
            edge_labels[(u, v)] = distance_network[u][v]
        
fig, ax = plt.subplots(figsize = (35, 35))

plt.figure(1)

nx.draw(G, pos = city_positions, with_labels = True, node_size = 1490, node_color = node_colors, 
        node_shape = "o", edge_color = edge_colors, font_size = 17, font_weight = "bold", 
        arrowsize = 20, arrowstyle = "->", font_color = "white", width = 3)

G.nodes["D"]["color"] = "red"

for veh in range(1, V+1):
    nx.draw_networkx_nodes(G, pos = city_positions, nodelist = nodes[veh], node_size = 1500, 
                           node_color = vehicle_colors[veh], label = f"Vehicle-{veh}")
nx.draw_networkx_edge_labels(G, pos = city_positions, edge_labels = edge_labels, 
                             label_pos = 0.5, font_size = 20)

plt.axis("on")
ax.tick_params(left = True, bottom = True, labelleft = True, labelbottom = True)
plt.title("Plot of CVRP of 16 Cities Solved by Genetic Algorithm")
plt.xticks(fontsize = 20)
plt.yticks(fontsize = 20)
plt.xlabel("X-Distance (km)", fontsize = 25)
plt.ylabel("Y-DIstance (km)", fontsize = 25)
plt.grid(linewidth = 3)
plt.legend(fontsize = 30, loc = "best")
plt.show()











# member = [0]

# curr = 0
# visit = {0}
# to_append = 0
# while len(member) != N+1:
#     mini = 10000
#     for n in range(0, N+1):
#         if n != curr and n not in visit:
#             if distance_network[n][curr] < mini:
#                 mini = distance_network[n][curr]
#                 to_append = n
#     member.append(to_append)
#     curr = to_append
#     visit.add(to_append)
#     to_append = 0


# def Crossover(self, parent1, parent2):
#     crossover_chromosome = Individual()
    
#     crossover_point = randint(2, N-2)
    
#     crossover_chromosome.genes[:crossover_point] = \
#         parent1.genes[:crossover_point]
    
#     visited = set(parent1.genes[:crossover_point])
    
#     for gene in parent2.genes:
#         if gene not in visited:
#             crossover_chromosome.genes.append(gene)
    
#     return crossover_chromosome








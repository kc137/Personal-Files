import math, random, numpy as np, networkx as nx, matplotlib.pyplot as plt, time, operator, heapq

# from random import shuffle, randint, uniform, random
from deap import base, creator, tools, benchmarks, algorithms

# Start Time

start = time.time()

# Necessary Constants

N = 16

colors = ["darkviolet", "limegreen", "darkorange", "magenta", "darkturquoise"]

coords_list = [(0, 0), (139, 120), (164, 167), (105, 155), (113, 185), 
               (-166, 143), (-176, 128), (-105, 160), (-105, 101), 
              (-180, -139), (-101, -150), (-189, -173), (-193, -110), 
              (188, -110), (167, -189), (113, -111), (127, -179)]

def get_distance(p1, p2):
    x = coords_list[p1][0] - coords_list[p2][0]
    y = coords_list[p1][1] - coords_list[p2][1]
    eucl_distance = round((x**2 + y**2)**0.5)
    return eucl_distance

distance_network = np.zeros([N+1, N+1], dtype = int)
demands = np.array([0, 15, 25, 34, 25, 20, 28, 17, 33, 25, 22, 19, 27, 20, 16, 21, 20])
capacity = 100

for p1 in range(N+1):
    for p2 in range(N+1):
        if p1 != p2:
            distance_network[p1][p2] = get_distance(p1, p2)

def generate_particle(s_min, s_max):
    particle_list = [n for n in range(1, N+1)]
    random.shuffle(particle_list)
    
    particle = creator.Particle(particle_list)
    particle.speed = [random.uniform(s_min, s_max) for _ in range(N)]
    particle.smin = s_min
    particle.smax = s_max
    return particle

def update_particle(particle, best, w, phi1, phi2):
    phi1_list = (random.uniform(0, phi1) for _ in range(N))
    phi2_list = (random.uniform(0, phi1) for _ in range(N))
    # Particle Best
    speeds_1 = map(operator.mul, phi1_list, map(operator.sub, particle.best, particle))
    # Neighbourhood Best
    speeds_2 = map(operator.mul, phi2_list, map(operator.sub, best, particle))
    
    # Update Speed
    particle.speed = list(map(operator.add, map(operator.mul, particle.speed, [w]*N), 
                              map(operator.add, speeds_1, speeds_2)))
    
    modified_particle = []
    
    # Speed Limits
    for speed in particle.speed:
        if speed < particle.smin:
            modified_particle.append(particle.smin)
        elif speed > particle.smax:
            modified_particle.append(particle.smax)
        else:
            modified_particle.append(speed)
    particle[:] = convert_particle(modified_particle)
    return

def get_fitness(particle):
    prev = 0
    cumu_load = 0
    distance = 0
    for loc in particle:
        if cumu_load + demands[loc] <= capacity:
            cumu_load += demands[loc]
            distance += distance_network[prev][loc]
            prev = loc
        
        else:
            cumu_load = demands[loc]
            distance += distance_network[prev][0]
            prev = 0
            distance += distance_network[prev][loc]
            prev = loc
    distance += distance_network[0][particle[-1]]        
    return (distance, )

def convert_particle(particle):
    enum_particle = [(val, idx) for idx, val in enumerate(particle)]
    heapq.heapify(enum_particle)
    validated_particle = []

    for _ in range(len(enum_particle)):
        location = heapq.heappop(enum_particle)[1]
        validated_particle.append(location + 1)

    return validated_particle

def run_pso(pop_size = 100, max_iterations = 300, weight = 0.8, phi1 = 0.5, phi2 = 0.4, max_s = 3.0):
    creator.create("Min_Fitness", base.Fitness, weights = (-1.0, ))
    creator.create("Particle", list, fitness = creator.Min_Fitness, 
                   speed = list, s_min = None, s_max = None, best = None)
    
    toolbox = base.Toolbox()
    toolbox.register("particle", generate_particle, s_min = -max_s, s_max = max_s)
    toolbox.register("population", tools.initRepeat, list, toolbox.particle)
    toolbox.register("update", update_particle, w = weight, phi1 = phi1, phi2 = phi2)
    toolbox.register("evaluate", get_fitness)
    
    popu = toolbox.population(n = pop_size)
    best = None
    iteration_no = 0
    prev_best = 10e5
    
    print("\nPSO is Starting...")
    # start = time.time()
    
    for gen in range(max_iterations):
        repeated = 0
        if gen % 100 == 0:
            print(f"Best till now : {best}")
        for part in popu:
            part.fitness.values = toolbox.evaluate(part)
            if part.fitness.values[0] < prev_best:
                prev_best = part.fitness.values[0]
                iteration_no = gen + 1
                print(iteration_no)
            elif part.fitness.values == prev_best:
                repeated += 1
        
        if repeated > int(np.ceil(0.20*pop_size)):
            alternate_popu = toolbox.population(n = pop_size)
            for particle in alternate_popu:
                particle.fitness.values = toolbox.evaluate(particle)
            some = int(np.ceil(0.1*pop_size))
            some_popu = tools.selRandom(alternate_popu, some)
            temp_popu = tools.selWorst(popu, pop_size - some)
        else:
            some = int(np.ceil(0.05*pop_size))
            some_popu = tools.selBest(popu, some)
            temp_popu = tools.selRandom(popu, pop_size - some)
        
        temp_popu = list(map(toolbox.clone, temp_popu))
        
        for particle in temp_popu:
            if not particle.best or particle.fitness < particle.best.fitness:
                particle.best = creator.Particle(particle)
                particle.best.fitness.values = particle.fitness.values
            if not best or particle.fitness < best.fitness:
                print(f"Actual - {particle}")
                best = creator.Particle(particle)
                print(f"Function - {best}")
                best.fitness.values = particle.fitness.values
        # print(best)
        for particle in temp_popu:
            toolbox.update(particle, best)

        temp_popu.extend(some_popu)
        popu[:] = temp_popu
    
    # end = time.time()
    print("\nPSO Ends...")
    best_particle = tools.selBest(popu, 1)[0]
    # best_particle = best
    print(f"\nBest Particle or Best Path : {best_particle}")
    best_solution = get_fitness(best_particle)[0]
    best_found = iteration_no
    print(f"\nBest Solution = {best_solution}")
    print(f"\nBest solution found in {best_found}-iterations.")
    # print("\nTotal time taken = {round(end - start, 3)} sec.")
    
    return best_particle, best_solution


run_pso()
        















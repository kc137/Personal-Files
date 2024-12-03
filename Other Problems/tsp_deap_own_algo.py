"""
This takes more time than eaSimple
"""

import random, matplotlib.pyplot as plt, scipy, numpy as np
from scipy.spatial.distance import pdist, squareform
from deap import base, creator, tools, algorithms
from copy import deepcopy

import warnings
warnings.filterwarnings("ignore")

import time

random.seed(7)

N = 20
len_popu = 200

coords = [(random.uniform(0, 50), random.uniform(0, 50)) for _ in range(N)]

matrix = np.round(squareform(pdist(coords)))

def fitness(indv):
    distance = 0
    
    for i in range(N-1):
        distance += matrix[indv[i]][indv[i+1]]
    distance += matrix[indv[-1]][indv[0]]
    
    return -distance, 

def sol_fitness(indv):
    distance = 0
    
    for i in range(N-1):
        distance += matrix[indv[i]][indv[i+1]]
        print(indv[i] + 1, indv[i+1] + 1)
    distance += matrix[indv[-1]][indv[0]]
    print(indv[-1] + 1, indv[0] + 1)
    
    return distance, 

def crossover(indv1, indv2):
    
    child1, child2 = indv1[:], indv2[:]
    
    idx1, idx2 = random.randint(2, N-2), random.randint(2, N-2)
    
    # if idx1 == idx2:
    #     while idx1 == idx2:
    #         idx2 = random.randint(2, N-2)
    
    if idx1 > idx2:
        idx1, idx2 = idx2, idx1
        
    child1[idx1:idx2 + 1] = indv2[idx1:idx2 + 1]
    child2[idx1:idx2 + 1] = indv1[idx1:idx2 + 1]
    
    visit1 = [False]*N
    visit2 = [False]*N
    
    visit1[idx1:idx2 + 1] = [True]*(idx2 - idx1 + 1)
    visit2[idx1:idx2 + 1] = [True]*(idx2 - idx1 + 1)
    
    new_i_1 = (idx2 + 1)
    new_i_2 = (idx2 + 1)
    
    for i in range(N):
        
        if not visit1[indv1[(new_i_1 + i) % N]]:
            child1[new_i_1] = indv1[new_i_1]
            new_i_1 = (new_i_1 + 1) % N
            visit1[indv1[new_i_1]] = True
        if not visit2[indv2[(new_i_2 + i) % N]]:
            child2[new_i_2] = indv2[new_i_2]
            new_i_2 = (new_i_2 + 1) % N
            visit2[indv2[new_i_2]] = True
    
    indv1.individual = child1
    indv2.individual = child2
    
    return indv1, indv2

start = time.time()

toolbox = base.Toolbox()

creator.create("FitnessMin", base.Fitness, weights = (1.0, ))
creator.create("Individual", list, fitness = creator.FitnessMin)
toolbox.register("indices", random.sample, range(N), N)
toolbox.register("individual", tools.initIterate, creator.Individual, toolbox.indices)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)
toolbox.register("evaluate", fitness)
toolbox.register("mate", crossover) # tools.cxPartialyMatched
toolbox.register("mutate", tools.mutInversion)
toolbox.register("select", tools.selTournament, tournsize = 5)
population = toolbox.population(n = 200)
cx_prob = 0.8
mut_prob = 0.2
n_gen = 100

stats = tools.Statistics(key = lambda indv : indv.fitness.values)
stats.register("max", np.max)
stats.register("min", np.min)
stats.register("mean", np.mean)
stats.register("sd", np.std)

def ga():
    
    population[:] = toolbox.select(population, k = len_popu)
    for indv in population:
        indv.fitness = toolbox.evaluate(indv)
    
    for gen in range(n_gen):
        
        len_elite = len_popu // 5
        elite = tools.selBest(population, len_elite)[:]
        population[:] = elite + tools.selTournament(population, 
                                                    k = len_popu - len_elite, 
                                                    tournsize = 5)
        # population[:] = elite + tools.selRandom(population, len_popu - len_elite)
        # population[:] = elite + tools.selRoulette(population, len_popu - len_elite)
        
        for i in range(0, len_popu, 2):
            
            indv1, indv2 = deepcopy(population[i]), deepcopy(population[i+1])
            
            if random.random() <= cx_prob:
                indv1.individual, indv2.individual = deepcopy(toolbox.mate(indv1, indv2))
            if random.random() <= mut_prob:
                indv1.individual = deepcopy(toolbox.mutate(indv1))
                indv2.individual = deepcopy(toolbox.mutate(indv2))
            
            # print(indv1.fitness, indv2.fitness)
            
            indv1.fitness = toolbox.evaluate(indv1)
            indv2.fitness = toolbox.evaluate(indv2)
            
            population[i] = deepcopy(indv1)
            population[i+1] = deepcopy(indv2)
            
        if gen % (len_popu // 10) == 0 and gen > 0:
            best_chromosome = tools.selBest(population, 1)
            print(best_chromosome[0].individual)
            print(-best_chromosome[0].fitness[0])
        

ga()

best_chromosome = tools.selBest(population, 5)

# for indv in best_chromosome:
#     one_indexed_indv = [n+1 for n in indv]
#     print(one_indexed_indv)
#     print(-indv.fitness[0])

end = time.time()

print(f"Time taken for GA using DEAP : {round(end - start, 3)} s.")

















"""
At Random Seed-7
coords = [(16.19163824165812, 7.542458696225096),
 (32.546723651992686, 3.621814333377138),
 (26.79410021533446, 18.28444584562928),
 (2.8999462387353403, 25.371786659471013),
 (1.874782922099244, 21.682284183119293),
 (3.492771178730947, 4.535650667193253),
 (21.225959457125697, 41.342606233601906),
 (6.190098057482279, 11.161948230350728),
 (31.371661120279466, 47.38544712285028),
 (28.855147430874933, 19.83402373253901),
 (48.812755279646005, 2.329134030887814),
 (42.923422952433974, 14.480464316583813),
 (7.212754167871877, 5.889611903918418),
 (15.424091205096719, 40.80631795600157),
 (9.036318996196874, 29.08000818312331),
 (31.945673446309204, 18.61987713628656),
 (27.38722328547789, 3.1394487486661573),
 (2.980058498311633, 10.297935640966326),
 (34.019998659089296, 21.379615283470145),
 (15.707358518839577, 29.278093175381937)]

def crossover(parent1, parent2):
    N1, N2 = N-1, N-1
    a = random.randint(2, N1-3)
    b = random.randint(2, N2-3)
    if a == b:
        while a == b:
            b = random.randint(2, N2-3)
    if a > b:
        a, b = b, a
    offspring1 = parent1[:]
    offspring2 = parent2[:]
    
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
    
    parent1.individual = offspring1
    parent2.individual = offspring2
    
    return parent1, parent2

sol_fitness(best_chromosome[0])
print(fitness([0, 12, 5, 17, 7, 4, 3,14, 19, 13, 6, 8, 9, 2, 15, 18, 11, 10, 1, 16]))
print(fitness([6, 0, 8, 5, 2, 3, 10, 19, 16, 13, 1, 14, 11, 4, 15, 7, 9, 17, 18, 12]))

"""






















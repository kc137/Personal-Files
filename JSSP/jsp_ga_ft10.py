import numpy as np, random, array
from collections import Counter
from numpy.random import randint
from deap import base, creator, tools
from jsp_ga_ft06_data import processing_times, machining_sequence
import plotly.figure_factory as ff

NJ = len(processing_times)
NM = len(processing_times[0])

ini_seq = [n for n in range(1, NJ + 1)]*(NM)

# def fitness(chromosome):
#     keys = {k : 0 for k in range(1, NJ + 1)}
#     j_time = {j : 0 for j in keys}
#     m_time = {m : 0 for m in range(1, NM+1)}
#     for j in chromosome:
#         # j = n % NJ if n % NJ else NJ
#         curr_m = machining_sequence[j][keys[j+1]]
#         processing_time = processing_times[j-1][keys[j+1]]
#         j_time[j+1] += processing_time
#         m_time[curr_m] += processing_time
        
#         j_time[j] = max(j_time[j+1], m_time[curr_m])
#         m_time[curr_m] = max(m_time[curr_m], j_time[j+1])
        
#         keys[j+1] += 1
        
#     makespan = max(j_time.values())
        
#     return (makespan, )

def fitness(chromosome):
    keys = {k : 0 for k in range(1, NJ+1)}
    j_time = {j : 0 for j in keys}
    m_time = {m : 0 for m in range(1, NM+1)}
    for n in chromosome:
        j = n % NJ if n % NJ else NJ
        curr_m = machining_sequence[j-1][keys[j]]
        processing_time = processing_times[j-1][keys[j]]
        j_time[j] += processing_time
        m_time[curr_m] += processing_time
        
        j_time[j] = max(j_time[j], m_time[curr_m])
        m_time[curr_m] = max(m_time[curr_m], j_time[j])
        
        keys[j] += 1
        
    makespan = max(j_time.values())
        
    return (makespan, )

# def crossover(ind1, ind2):
#     N1, N2 = len(ind1), len(ind2)
#     child1, child2 = [0 for _ in range(N1)], [0 for _ in range(N2)]
#     visit1, visit2 = [0 for _ in range(N1+1)], [0 for _ in range(N2+1)]
#     idx1, idx2 = randint(0, N2), randint(0, N2)
#     while idx1 == idx2:
#         idx2 = randint(0, N2)
    
#     for idx in range(idx1, idx2 + 1):
#         child1[idx] = ind1[idx]
#         child2[idx] = ind2[idx]
#         visit1[ind1[idx]] = 1
#         visit2[ind2[idx]] = 1
    
#     n1 = 0
#     for i in range(N1):
#         if visit1[ind2[i]]:
#             continue
#         if n1 == idx1:
#             n1 = idx2 + 1
#         child1[n1] = ind2[i]
#         visit1[ind2[i]] = 1
#         n1 += 1
    
#     n2 = 0
#     for i in range(N2):
#         if visit2[ind1[i]]:
#             continue
#         if n2 == idx1:
#             n2 = idx2 + 1
#         child2[n2] = ind1[i]
#         visit2[ind1[i]] = 1
#         n2 += 1

#     return child1, child2

def repair(ind):
    
    ctr_seq = Counter(ind)
    excess = []
    less = []

    for k, v in ctr_seq.items():
        if v == NJ:
            continue
        elif v > NJ:
            to_reduce = [k]*(v-NJ)
            excess.extend(to_reduce)
        else:
            to_add = [k]*(NJ-v)
            less.extend(to_add)
            
    new_seq = ind[:]

    for j in range(len(new_seq)):
        if not excess:
            break
        if ind[j] == excess[-1]:
            # print(j)
            new_seq[j] = less[-1]
            excess.pop()
            less.pop()
    return new_seq

def crossover(ind1, ind2):
    N = len(ind1)
    child1 = ind1[:]
    child2 = ind2[:]
    cutpoint = np.random.choice(range(1, N+1), 2, replace = False)
    child1[cutpoint[0]:cutpoint[1]] = ind2[cutpoint[0]:cutpoint[1]]
    child2[cutpoint[0]:cutpoint[1]] = ind1[cutpoint[0]:cutpoint[1]]
    fixed_child1 = repair(child1)
    fixed_child2 = repair(child1)
    return fixed_child1, fixed_child2, 

def mutation(ind, indpb):
    N = len(ind)
    for i in range(N):
        if random.random() < indpb:
            swap_indx = random.randint(0, N - 2)
            if swap_indx >= i:
                swap_indx += 1
            ind[i], ind[swap_indx] = ind[swap_indx], ind[i]

    return ind,
    
class GeneticAlgorithm:
    
    def __init__(self, population_size = 300, 
                 crossover_rate = 0.8, 
                 mutation_rate = 0.1, 
                 n_gen = 300):
        self.population_size = population_size
        self.crossover_rate = crossover_rate
        self.mutation_rate = mutation_rate
        self.n_gen = n_gen
        self.best_solution = []
        self.toolbox = base.Toolbox()
        self.create_creators()
    
    def create_creators(self):
        creator.create("FitnessMin", base.Fitness, weights = (-1.0, ))
        creator.create("Individual", list, fitness = creator.FitnessMin)
        # creator.create("Individual", array.array, typecode = "b", fitness = creator.FitnessMin)
        
        # Registering Toolbox
        self.toolbox.register("indexes", 
                              random.sample, 
                              ini_seq, NM*NJ)
        # self.toolbox.register("indexes", 
        #                       list, 
        #                       final_sol)
        
        # Creating individual and population from each Individual
        self.toolbox.register("individual", tools.initIterate, 
                              creator.Individual, self.toolbox.indexes)
        self.toolbox.register("population", tools.initRepeat, 
                              list, self.toolbox.individual)
        
        # Adding Fitness Evaluation function in tools
        self.toolbox.register("eval_fitness", fitness)
        
        # Selection Method
        self.toolbox.register("selection", tools.selRoulette)
        
        # Crossover Method
        self.toolbox.register("ox_crossover", crossover)
        
        # Mutation Method
        self.toolbox.register("mutation", mutation, self.mutation_rate)
            
    def run_gen_algo(self):
        gen = -1
        self.popu = self.toolbox.population(n = self.population_size)
        self.remaining_ones = [indv for indv in self.popu if not indv.fitness.valid]
        self.fitnesses = list(map(self.toolbox.eval_fitness, self.remaining_ones))
        for indv, fitness_value in zip(self.popu, self.fitnesses):
            indv.fitness.values = fitness_value
        best_sol = 99999999
        
        while gen != self.n_gen:
            gen += 1
            self.offspring = tools.selTournament(self.popu, self.population_size, 2)
            self.offspring = [self.toolbox.clone(ind) for ind in self.offspring]
            
            # Now performing crossover and mutations according to prob.
            for ind1, ind2 in zip(self.offspring[::2], self.offspring[1::2]):
                if random.random() <= self.crossover_rate:
                    self.toolbox.ox_crossover(ind1, ind2)
                    # print(ind1, ind2)
                    del ind1.fitness.values, ind2.fitness.values
            
            # for ind in self.offspring:
            #     self.toolbox.mutation(ind)
            #     del ind.fitness.values
            
            invalid_ind = [ind for ind in self.offspring if not ind.fitness.valid]
            fitnesses = self.toolbox.map(self.toolbox.eval_fitness, invalid_ind)
            for ind, fit in zip(invalid_ind, fitnesses):
                ind.fitness.values = fit
            
            # Replace Population by Offspring
            self.popu = self.toolbox.selection(self.popu + self.offspring, self.population_size)
            
            # Evaluate New Population
            for ind in self.popu:
                ind.fitness.values = self.toolbox.eval_fitness(ind)
                if ind.fitness.values[0] < best_sol:
                    best_sol = ind.fitness.values[0]
                    best_one = ind
            
            best_makespan = best_sol
            
            if gen % 50 == 0:
                best_one_mod = []
                print(best_one)
                for gene in best_one:
                    if gene % NJ:
                        best_one_mod.append(gene % NJ)
                    else:
                        best_one_mod.append(NJ)
                print(f"Generation No.-{gen}"
                      f"\nBest Seq : {best_one_mod}"
                      f"\nMakespan : {best_makespan}")
        self.best_solution = best_one[:]
    
    def get_best_one(self):
        return self.best_solution
        
GA = GeneticAlgorithm(60, 0.6, 0.3, 1000)
GA.create_creators()
GA.run_gen_algo()

"""
Best = 2-1-1-3-3-2-6-3-5-6-2-6-4-4-5-4-1-3-4-5-6-3-4-2-1-3-5-1-6-4-2-1-2-5-5-6
"""

# final_sol = [2,
#  1,
#  1,
#  3,
#  3,
#  2,
#  6,
#  3,
#  5,
#  6,
#  2,
#  6,
#  4,
#  4,
#  5,
#  4,
#  1,
#  3,
#  4,
#  5,
#  6,
#  3,
#  4,
#  2,
#  1,
#  3,
#  5,
#  1,
#  6,
#  4,
#  2,
#  1,
#  2,
#  5,
#  5,
#  6]

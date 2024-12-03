import random
from copy import deepcopy

flights_dict = {}
cities_set = set()
destination = "FCO"

seed = random.randint(0, 70)
seed = 66
random.seed(seed)

with open("flights.txt") as data:
    lines = data.read().splitlines()
    
    for line in lines:
        plan = line.split(",")
        origin, dest, dept_time, arri_time, price = plan
        flights_dict.setdefault((origin, dest), [])
        
        flights_dict[(origin, dest)].append((dept_time, arri_time, int(price)))
        if origin != "FCO":
            cities_set.add(origin)

N = len(flights_dict)
flight_len = 10

class Individual:
    
    def __init__(self):
        self.chromosome = [random.randint(0, flight_len - 1) for _ in range(N)]
        self.fitness = 0
        
        i = 0
        for flight in flights_dict:
            self.fitness += flights_dict[flight][self.chromosome[i]][2]
            # print(f"{flight} : {flights_dict[flight][self.chromosome[i]][2]}")
            i += 1
        return
    
    def update_fitness(self):
        self.fitness = 0
        i = 0
        for flight in flights_dict:
            self.fitness += flights_dict[flight][self.chromosome[i]][2]
            # print(f"{flight} : {flights_dict[flight][self.chromosome[i]][2]}")
            i += 1
        return

class GeneticAlgorithm:
    
    def __init__(self, cx_prob, mut_prob, pop_size, generations):
        self.pop_size = pop_size
        self.population = [Individual() for _ in range(self.pop_size)]
        self.cx_prob = cx_prob
        self.mut_prob = mut_prob
        self.generations = generations
        self.best_individual = None
        self.best_fitness = float("inf")
        self.best_generation = 0
    
    @staticmethod
    def single_point_crossover(indi1, indi2):
        
        seperation_idx = random.randint(1, N-2)
        
        indi1[seperation_idx + 1:], indi2[seperation_idx + 1:] = indi2[seperation_idx + 1:], indi1[seperation_idx + 1:]
        
        return indi1, indi2
    
    def mutation(self, indv):
        new_indv = indv[:]
        for i in range(len(indv)):
            if random.random() <= self.mut_prob:
                swap_idx_1 = random.randint(0, N-2)
                swap_idx_2 = random.randint(0, N-2)
                if swap_idx_1 > swap_idx_2:
                    swap_idx_1, swap_idx_2 = swap_idx_2, swap_idx_2
                new_indv[:swap_idx_1] = indv[:swap_idx_1]
                new_indv[swap_idx_2:] = indv[swap_idx_2:]
                new_indv[swap_idx_1:swap_idx_2] = indv[swap_idx_1:swap_idx_2][::-1]
        return indv
    
    @staticmethod
    def tournament_selection(popu, k, tourn_size):
        selected = []
        for _ in range(k):
            combatants = [random.choice(popu) for _ in range(tourn_size)]
            selected.append(min(combatants, key = lambda indv : indv.fitness))
        return selected
    
    def run(self):
        self.new_popu = deepcopy(self.population)
        self.new_popu.sort(key = lambda indv : indv.fitness)
        # self.temp_popu = deepcopy(self.new_popu)
        self.best_solution = min(self.new_popu, key = lambda indv : indv.fitness)
        self.best_fitness = self.best_solution.fitness
        self.best_generation = 0
        
        for curr_gen in range(self.generations):
            elites = self.new_popu[:int(0.5*self.pop_size)]
            k_sel = int(0.0*(self.pop_size))
            remaining_size = self.pop_size - k_sel - len(elites)
            selected_individuals = self.tournament_selection(self.new_popu, 
                                                              k = k_sel, 
                                                              tourn_size = 3)
            # remaining_individuals = [Individual() for _ in range(remaining_size)]
            remaining_individuals = [random.choice(self.new_popu) for _ in range(remaining_size)]
            
            brand_new_popu = elites[:] + selected_individuals[:] + remaining_individuals[:]
            
            
            for i in range(0, self.pop_size, 2):
                indv1 = deepcopy(brand_new_popu[i])
                indv2 = deepcopy(brand_new_popu[i+1])
                
                new_chromosome_1, new_chromosome_2 = self.single_point_crossover(indv1.chromosome, 
                                                                                 indv2.chromosome)
                
                indv1.chromosome = deepcopy(self.mutation(new_chromosome_1))
                indv2.chromosome = deepcopy(self.mutation(new_chromosome_1))
                
                indv1.update_fitness()
                indv2.update_fitness()
                
                brand_new_popu[i] = deepcopy(indv1)
                brand_new_popu[i+1] = deepcopy(indv2)
            
            self.new_popu = deepcopy(brand_new_popu)
            self.new_popu.sort(key = lambda indv : indv.fitness)
            
            curr_gen_best = min(self.new_popu, key = lambda indv : indv.fitness)
            
            if curr_gen_best.fitness < self.best_fitness:
                self.best_solution = deepcopy(curr_gen_best)
                self.best_fitness = curr_gen_best.fitness
                self.best_generation = curr_gen
            
            ten_cent = self.generations // 10
            if (curr_gen % ten_cent) == 0:
                print(f"Current generation best cost : {curr_gen_best.fitness}$")
                print(f"Best cost till now : {self.best_fitness}$")
        
        print(f"The best solution found by GA for flight scheduling problem : {self.best_fitness}$")
        print(f"Best solution found with seed-{seed} at Generation-{self.best_generation}")
        

ga = GeneticAlgorithm(cx_prob = 0.75, 
                      mut_prob = 0.2, 
                      pop_size = 700, 
                      generations = 50)
ga.run()

"""
Elites - 50%
Seed - 48, 65, 39, 66
ga = GeneticAlgorithm(cx_prob = 0.75, 
                      mut_prob = 0.2, 
                      pop_size = 700, 
                      generations = 50)

Best cost till now : 1566$
The best solution found by GA for flight scheduling problem : 1566$
Best solution found with seed-48 at Generation-34
"""

"""
ga = GeneticAlgorithm(cx_prob = 0.85, 
                      mut_prob = 0.3, 
                      pop_size = 300, 
                      generations = 300)
Best cost till now : 1566$
The best solution found by GA for flight scheduling problem : 1566$
Best solution found at Generation-30
"""

"""
ga = GeneticAlgorithm(cx_prob = 0.75, 
                      mut_prob = 0.2, 
                      pop_size = 300, 
                      generations = 100)
Best cost till now : 1566$
The best solution found by GA for flight scheduling problem : 1566$
Best solution found at Generation-34
"""

"""
ga = GeneticAlgorithm(cx_prob = 0.75, 
                      mut_prob = 0.2, 
                      pop_size = 500, 
                      generations = 100)
The best solution found by GA for flight scheduling problem : 1566$
Best solution found at Generation-27
"""

"""
ga = GeneticAlgorithm(cx_prob = 0.75, 
                      mut_prob = 0.2, 
                      pop_size = 700, 
                      generations = 50)
Best cost till now : 1566$
The best solution found by GA for flight scheduling problem : 1566$
Best solution found at Generation-25
"""
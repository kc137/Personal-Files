import random
from copy import deepcopy

# random.seed(13)
N = 14

class Product:
    
    def __init__(self, name, space, price, quantity):
        self.name = name
        self.space = space
        self.price = price
        self.quantity = quantity

products_list = [('Refrigerator A', 0.751, 999.90, 1), 
            ('Cell phone', 0.0000899, 2199.12, 5), 
            ('TV 55', 0.400, 4346.99, 2), 
            ('TV 50', 0.290, 3999.90, 3), 
            ('TV 42', 0.200, 2999.00, 4), 
            ('Notebook A', 0.00350, 2499.90, 1), 
            ('Ventilador', 0.496, 199.90, 10), 
            ('Microwave A', 0.0424, 308.66, 2), 
            ('Microwave B', 0.0544, 429.90, 5), 
            ('Microwave C', 0.0319, 299.29, 3), 
            ('Refrigerator B', 0.635, 849.00, 2), 
            ('Refrigerator C', 0.870, 1199.89, 6), 
            ('Notebook B', 0.498, 1999.90, 2), 
            ('Notebook C', 0.527, 3999.00, 1)]

products = []

for name, space, price, qty in products_list:
    products.append(Product(name, space, price, qty))

names  = []
spaces = []
prices = []
quantities = []

for prod in products:
    for _ in range(prod.quantity):
        names.append(prod.name)
        spaces.append(prod.space)
        prices.append(prod.price)

N = len(names)

class Individual:
    
    def __init__(self):
        self.chromosome = [random.randint(0, 1) for i in range(N)]
        self.space = 0
        self.score = 0
    
        for i in range(N):
            if self.chromosome[i]:
                self.space += spaces[i]
                self.score += prices[i]
        
        self.score = self.score if self.space <= 10 else 1
            

class GeneticAlgorithm:
    
    def __init__(self, space_limit, cx_prob, mut_prob, pop_size, generations):
        self.space_limit = space_limit
        self.cx_prob = cx_prob
        self.mut_prob = mut_prob
        self.pop_size = pop_size
        self.generations = generations
        self.population = [Individual() for _ in range(pop_size)]
        self.best_solution = None
        self.best_fitness = 0
        self.best_generation = 0
    
    @staticmethod
    def single_point_crossover(ind1, ind2):
        child1 = ind1[:]
        child2 = ind2[:]
        seperation_idx = random.randint(1, N-2)
        child1[seperation_idx + 1:] = ind2[seperation_idx + 1:]
        child2[seperation_idx + 1:] = ind1[seperation_idx + 1:]
        
        return child1, child2
    
    def mutation(self, ind):
        for i in range(N):
            if random.random() <= self.mut_prob:
                ind[i] = 0 if ind[i] else 1
        
        return ind
    
    def roulette_wheel_selection(self, total_sum, population):
        cumu_sum = 0
        sum_desired = random.random()*total_sum
        
        for i in range(self.pop_size):
            cumu_sum += population[i].score
            if sum_desired <= cumu_sum:
                return population[i]
        # return population[i]
    
    def run(self):
        self.new_popu = deepcopy(self.population)
        self.new_popu = sorted(self.new_popu, 
                               key = lambda indi : indi.score, 
                               reverse = True)
        self.temp_popu = deepcopy(self.new_popu)
        
        self.best_solution = self.new_popu[0]
        self.best_fitness = self.new_popu[0].score
        self.best_generation = 0
        
        curr_gen = 0
        
        fitnesses = []
        for indi in self.new_popu:
            fitnesses.append((indi.score, indi.space))
        print(fitnesses)
        
        while curr_gen < self.generations:
            total_sum = sum([indi.score for indi in self.new_popu])
            
            for i in range(0, self.pop_size, 2):
                if i + 1 <= self.pop_size // 10:
                    indi1 = self.roulette_wheel_selection(total_sum, self.new_popu)
                    indi2 = self.roulette_wheel_selection(total_sum, self.new_popu)
                # print(indi1, indi2)
                else:
                    indi1 = Individual()
                    indi2 = Individual()
                
                if random.random() <= self.cx_prob:
                    # 2-Children
                    new_chromosome_1, new_chromosome_2 = self.single_point_crossover(indi1.chromosome, indi2.chromosome)
                    
                    indi1.chromosome = deepcopy(self.mutation(new_chromosome_1))
                    indi2.chromosome = deepcopy(self.mutation(new_chromosome_2))
                    
                # indi1.score = indi1.score if indi1.space <= self.space_limit else 1
                # indi2.score = indi2.score if indi2.space <= self.space_limit else 1
                
                
                self.temp_popu[i] = deepcopy(indi1)
                self.temp_popu[i+1] = deepcopy(indi2)
                
                # print(self.temp_popu == self.new_popu)
            
            self.new_popu = deepcopy(self.temp_popu)
            self.new_popu = sorted(self.new_popu, 
                                   key = lambda indi : indi.score, 
                                   reverse = True)
            
            curr_gen_best = self.new_popu[0].score
            
            
            if curr_gen_best >= self.best_fitness:
                self.best_fitness = curr_gen_best
                self.best_solution = deepcopy(self.new_popu[0])
                self.best_generation = curr_gen
            curr_gen += 1
            
            if curr_gen % 10 == 0:
                print(f"Current solution at Gen-{curr_gen} : {self.new_popu[0].score}")
                print(f"Best solution so far at Gen-{curr_gen} : {self.best_fitness}")
        
        print(f"The best solution found by GA for Knapsack problem : {self.best_fitness}$")
        print(f"Best solution found at Generation-{self.best_generation}")
        
        return self.best_solution
    

ga = GeneticAlgorithm(space_limit = 10, 
                      cx_prob = 0.85, 
                      mut_prob = 0.03, 
                      pop_size = 300, 
                      generations = 300)
ga.run()

ans = ga.best_solution

print(ans.score, ans.space, ans.chromosome)

"""
ga = GeneticAlgorithm(space_limit = 10, 
                      cx_prob = 0.85, 
                      mut_prob = 0.03, 
                      pop_size = 300, 
                      generations = 300)
Best solution found at Generation-277
59313.20000000001 9.9211596 [0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 1, 1, 0, 1, 0, 1, 0, 0, 0, 0, 1, 0, 1, 0, 1]
"""
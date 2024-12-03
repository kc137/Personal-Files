import random, numpy
from deap import base, creator, tools, algorithms

flights_dict = {}
cities_set = set()
destination = "FCO"

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

def create_gene():
    return random.randint(0, flight_len - 1)

def fitness_function(indv):
    cost = 0
    
    i = 0
    for flight in flights_dict:
        cost += flights_dict[flight][indv[i]][2]
        i += 1
    return cost, 
    
toolbox = base.Toolbox()
creator.create('FitnessMin', base.Fitness, weights=(-1.0,))
creator.create('Individual', list, fitness=creator.FitnessMin)
toolbox.register('individual', tools.initRepeat, creator.Individual, create_gene, n=12)
toolbox.register('population', tools.initRepeat, list, toolbox.individual)
toolbox.register('evaluate', fitness_function)
toolbox.register('mate', tools.cxTwoPoint)
toolbox.register('mutate', tools.mutInversion) # indpb = 0.05
toolbox.register('select', tools.selTournament, tournsize=3)
population = toolbox.population(n = 200)
crossover_probability = 0.8
mutation_probability = 0.3
number_of_generations = 50

statistics = tools.Statistics(key=lambda individuo: individuo.fitness.values)
statistics.register("max", numpy.max)
statistics.register("min", numpy.min)
statistics.register("med", numpy.mean)
statistics.register("std", numpy.std)

population, info = algorithms.eaSimple(population, toolbox,
                                       crossover_probability, mutation_probability,
                                       number_of_generations, statistics)

best_solution = tools.selBest(population, 1)
for individual in best_solution:
  print(individual)
  print(individual.fitness)


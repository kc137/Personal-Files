import random, warnings, numpy as np
from deap import base, creator, tools, algorithms

warnings.filterwarnings("ignore")

seed = random.randint(0, 700)
random.seed(seed)

nurses = 12
days = 7
shifts = 3
N = nurses*days*shifts
len_popu = 2000

nurse_req = [[3, 4], [3, 4], [2, 3]]

shift_pref = [[1, 0, 1], [0, 1, 0], [0, 0, 1], [1, 1, 1], 
              [0, 1, 1], [1, 0, 1], [1, 1, 1], [0, 0, 1], 
              [0, 1, 0], [1, 1, 0], [0, 1, 1], [1, 0, 0]]

def random_int():
    return random.randint(0, 1)

def staff_violations(indv):
    violations_s1 = 0
    violations_s2 = 0
    violations_s3 = 0
    for s in range(0, shifts*days, shifts):
        staff_s1 = sum([indv[s + i] for i in range(0, N, shifts*days)])
        staff_s2 = sum([indv[s + i] for i in range(1, N, shifts*days)])
        staff_s3 = sum([indv[s + i] for i in range(2, N, shifts*days)])
                
        if staff_s1 < nurse_req[0][0] or staff_s1 > nurse_req[0][1]:
            violations_s1 += 10
        if staff_s2 < nurse_req[1][0] or staff_s2 > nurse_req[1][1]:
            violations_s2 += 10
        if staff_s3 < nurse_req[2][0] or staff_s3 > nurse_req[2][1]:
            violations_s3 += 10
    
    return violations_s1 + violations_s2 + violations_s3

def shift_violations(indv):
    
    violations = 0
    n = shifts*days
    for i in range(0, N, shifts):
        # print(i, n)
        shift_1, shift_2, shift_3 = indv[i], indv[i+1], indv[i+2]
        if shift_pref[i // n][0] == 0 and shift_pref[i // n][0] != shift_1:
            violations += 10
        if shift_pref[i // n][1] == 0 and shift_pref[i // n][1] != shift_2:
            violations += 10
        if shift_pref[i // n][2] == 0 and shift_pref[i // n][2] != shift_3:
            violations += 10
        
    return violations

def week_shift_violations(indv):
    violations = 0
    for i in range(0, N, shifts*days):
        if sum(indv[i:shifts*days + i]) > 5:
            violations += 10
    return violations

def consecutive_violations(indv):
    violations = 0
    for i in range(0, N, shifts*days):
        check = indv[i:shifts*days + i]
        for j in range(0, shifts*days, shifts):
            shift_1, shift_2, shift_3 = check[j], check[j+1], check[j+2]
            if shift_1 and shift_1 == shift_2:
                violations += 10
            if shift_2 and shift_2 == shift_3:
                violations += 10
    return violations

def fitness_fn(indv):
    total_violations = (staff_violations(indv) 
                        + shift_violations(indv) 
                        + week_shift_violations(indv) 
                        + consecutive_violations(indv))
    return total_violations, 

hof = tools.HallOfFame(len_popu // 10)

toolbox = base.Toolbox()

creator.create("FitnessMin", base.Fitness, weights = (-1.0, ))
creator.create("Individual", list, fitness = creator.FitnessMin)
toolbox.register("individual", tools.initRepeat, creator.Individual, random_int, n = N)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)
toolbox.register("evaluate", fitness_fn)
toolbox.register("mate", tools.cxTwoPoint)
toolbox.register("mutate", tools.mutFlipBit, indpb = 0.04)
toolbox.register("select", tools.selTournament, tournsize = 4)
# toolbox.register("select", tools.selRoulette)

population = toolbox.population(n = len_popu)
cx_prob = 0.85
mut_prob = 0.12
n_gen = 150

statistics = tools.Statistics(key = lambda indv : indv.fitness.values)
statistics.register("max", np.max)
statistics.register("min", np.min)
statistics.register("mean", np.mean)
statistics.register("std", np.std)

# population, logbook = eaSimpleWithElitism(population = population, 
#                                           toolbox = toolbox, 
#                                           cxpb = cx_prob, 
#                                           mutpb = mut_prob, 
#                                           ngen = n_gen, 
#                                           stats = statistics, 
#                                           halloffame = hof)

population, logbook = algorithms.eaSimple(population, 
                                          toolbox, 
                                          cx_prob, 
                                          mut_prob, 
                                          n_gen, 
                                          statistics)

best = tools.selBest(population, 1)

nurses_schedule = []

for indv in best:
    print(indv)
    print(staff_violations(indv))
    print(shift_violations(indv))
    print(week_shift_violations(indv))
    print(consecutive_violations(indv))
    # print(indv)

    for i in range(0, N, shifts*days):
        nurses_schedule.append(indv[i:shifts*days + i])

print(nurses_schedule)
print(f"Seed-{seed}")
























# target_array = [[[0, 0, 0],
#         [0, 0, 0],
#         [0, 0, 0],
#         [0, 0, 0],
#         [0, 0, 0],
#         [1, 0, 1],
#         [1, 0, 1]],

#        [[0, 0, 0],
#         [0, 0, 0],
#         [0, 0, 0],
#         [0, 0, 0],
#         [0, 1, 0],
#         [0, 1, 0],
#         [0, 1, 0]],

#        [[0, 0, 1],
#         [0, 0, 1],
#         [0, 0, 1],
#         [0, 0, 1],
#         [0, 0, 1],
#         [0, 0, 0],
#         [0, 0, 0]],

#        [[1, 0, 0],
#         [1, 0, 0],
#         [1, 0, 1],
#         [0, 0, 0],
#         [0, 0, 0],
#         [0, 0, 0],
#         [0, 0, 0]],

#        [[0, 1, 0],
#         [0, 1, 0],
#         [0, 1, 0],
#         [0, 1, 0],
#         [0, 1, 0],
#         [0, 0, 0],
#         [0, 0, 0]],

#        [[1, 0, 0],
#         [1, 0, 0],
#         [1, 0, 0],
#         [1, 0, 1],
#         [0, 0, 0],
#         [0, 0, 0],
#         [0, 0, 0]],

#        [[0, 1, 0],
#         [0, 1, 0],
#         [0, 1, 0],
#         [1, 0, 0],
#         [1, 0, 0],
#         [0, 0, 0],
#         [0, 0, 0]],

#        [[0, 0, 1],
#         [0, 0, 1],
#         [0, 0, 0],
#         [0, 0, 0],
#         [0, 0, 1],
#         [0, 0, 1],
#         [0, 0, 1]],

#        [[0, 1, 0],
#         [0, 0, 0],
#         [0, 0, 0],
#         [0, 1, 0],
#         [0, 1, 0],
#         [0, 1, 0],
#         [0, 1, 0]],

#        [[1, 0, 0],
#         [1, 0, 0],
#         [0, 0, 0],
#         [0, 0, 0],
#         [1, 0, 0],
#         [1, 0, 0],
#         [1, 0, 0]],

#        [[0, 0, 0],
#         [0, 1, 0],
#         [0, 1, 0],
#         [0, 1, 0],
#         [0, 0, 0],
#         [0, 1, 0],
#         [0, 1, 0]],

#        [[0, 0, 0],
#         [0, 0, 0],
#         [1, 0, 0],
#         [1, 0, 0],
#         [1, 0, 0],
#         [1, 0, 0],
#         [1, 0, 0]]]

# target = []

# for arr in target_array:
#     for sub_arr in arr:
#         target += sub_arr
    
# print(target)
# print(staff_violations(target))
# print(shift_violations(target))
# print(week_shift_violations(target))
# print(consecutive_violations(target))

# target_schedule = []

# for i in range(0, N, shifts*days):
#     target_schedule.append(target[i:shifts*days + i])
    
# target_1 = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0]

# print(target_1)
# target_schedule_1 = []
# for i in range(0, N, shifts*days):
#     target_schedule_1.append(target_1[i:shifts*days + i])
    
# print(staff_violations(target_1))
# print(shift_violations(target_1))
# print(week_shift_violations(target_1))
# print(consecutive_violations(target_1))

"""
def eaSimpleWithElitism(population, toolbox, cxpb, mutpb, ngen, stats=None,
             halloffame=None, verbose=__debug__):
    \"""This algorithm is similar to DEAP eaSimple() algorithm, with the modification that
    halloffame is used to implement an elitism mechanism. The individuals contained in the
    halloffame are directly injected into the next generation and are not subject to the
    genetic operators of selection, crossover and mutation.
    \"""
    logbook = tools.Logbook()
    logbook.header = ['gen', 'nevals'] + (stats.fields if stats else [])

    # Evaluate the individuals with an invalid fitness
    invalid_ind = [ind for ind in population if not ind.fitness.valid]
    fitnesses = toolbox.map(toolbox.evaluate, invalid_ind)
    for ind, fit in zip(invalid_ind, fitnesses):
        ind.fitness.values = fit

    if halloffame is None:
        raise ValueError("halloffame parameter must not be empty!")

    halloffame.update(population)
    hof_size = len(halloffame.items) if halloffame.items else 0

    record = stats.compile(population) if stats else {}
    logbook.record(gen=0, nevals=len(invalid_ind), **record)
    if verbose:
        print(logbook.stream)

    # Begin the generational process
    for gen in range(1, ngen + 1):

        # Select the next generation individuals
        offspring = toolbox.select(population, len(population) - hof_size)

        # Vary the pool of individuals
        offspring = algorithms.varAnd(offspring, toolbox, cxpb, mutpb)

        # Evaluate the individuals with an invalid fitness
        invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
        fitnesses = toolbox.map(toolbox.evaluate, invalid_ind)
        for ind, fit in zip(invalid_ind, fitnesses):
            ind.fitness.values = fit

        # add the best back to population:
        offspring.extend(halloffame.items)

        # Update the hall of fame with the generated individuals
        halloffame.update(offspring)

        # Replace the current population by the offspring
        population[:] = offspring

        # Append the current generation statistics to the logbook
        record = stats.compile(population) if stats else {}
        logbook.record(gen=gen, nevals=len(invalid_ind), **record)
        if verbose:
            print(logbook.stream)

    return population, logbook

"""
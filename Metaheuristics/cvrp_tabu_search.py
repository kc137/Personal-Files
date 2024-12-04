import random, numpy as np
from scipy.spatial.distance import pdist, squareform
from copy import deepcopy

"""
Two methods can be implemented with and without neighbourhood
"""

N = 17
seed = 7
# random.seed(seed)

coords = [(random.randint(0, 50), random.randint(0, 50)) for _ in range(N)]

distance_matrix = np.round(squareform(pdist(coords)))

demands = [0, 1, 1, 2, 4, 2, 4, 8, 8, 1, 2, 1, 2, 4, 4, 8, 8]
capacity = 15


def gen_initial_solution():
    new_state = [0]
    visit = set([0])
    for i in range(N-1):
        min_dist, city = min([(dist, i) for i, dist in enumerate(distance_matrix[new_state[-1]])
                            if i != new_state[-1] and i not in visit])
        new_state.append(city)
        visit.add(city)
    
    return new_state
        

# neighbourhood_size = 1000
max_tabu_size = 100
max_iterations = 200
initial_state = gen_initial_solution()
initial_state = list(range(N))
random.shuffle(initial_state)

def two_opt_swap(state, idx1, idx2):
    
    new_state = state[:]
    new_state[idx1:idx2 + 1] = state[idx1:idx2 + 1][::-1]
    
    return new_state

# def get_neighbours(state):
#     neighbours = []
#     for _ in range(neighbourhood_size):
#         new_state, idx1, idx2 = two_opt_swap(state)
#         neighbours.append([new_state, idx1, idx2])
        
#     return neighbours

def fitness(state):
        distance, cum_demand = 0, 0
        prev = 0
        
        for loc in state:
            if cum_demand + demands[loc] <= capacity:
                distance += distance_matrix[prev][loc]
                cum_demand += demands[loc]
                prev = loc
            else:
                distance += distance_matrix[prev][0]
                cum_demand = demands[loc]
                prev = 0
                distance += distance_matrix[prev][loc]
                prev = loc
        distance += distance_matrix[loc][0]
        return distance

def tabu_search():
    best_state = initial_state[:]
    best_fitness = fitness(best_state)
    print(best_state, best_fitness)
    tabu_list = []
    len_tl = 0
    tabu_set = set()
    iteration = 0
    # best_indices = None
    # best_improvement = float("inf")
    
    while iteration < max_iterations:
        best_indices = None
        
        for i in range(N-1):
            for j in range(i+1, N):
                if i != j:
                    n_state = two_opt_swap(best_state, i, j)[:]
                    
                    if (i, j) not in tabu_set and fitness(n_state) < best_fitness:
                        best_state = deepcopy(n_state)
                        best_fitness = fitness(best_state)
                        best_indices = (i, j)
                        
        if best_indices:
            tabu_list.append(best_indices)
            tabu_set.add(best_indices)
            len_tl += 1
            
            if len_tl >= max_tabu_size:
                indices = tabu_list.pop(0)
                tabu_set.remove(indices)
                len_tl -= 1
        
        iteration += 1
        if iteration % 50 == 0:
            print(f"Iteration-{iteration}")
            print(best_state, best_fitness)
            # print(tabu_list)
    
    print(best_state, best_fitness)
    return best_state        
                
res = tabu_search()

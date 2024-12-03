import numpy as np
from numpy.random import randint
from random import random, shuffle

matrix = [
      [0, 548, 776, 696, 582, 274, 502, 194, 308, 194, 536, 502, 388, 354, 468, 776, 662],
      [548, 0, 684, 308, 194, 502, 730, 354, 696, 742, 1084, 594, 480, 674, 1016, 868, 1210],
      [776, 684, 0, 992, 878, 502, 274, 810, 468, 742, 400, 1278, 1164, 1130, 788, 1552, 754],
      [696, 308, 992, 0, 114, 650, 878, 502, 844, 890, 1232, 514, 628, 822, 1164, 560, 1358],
      [582, 194, 878, 114, 0, 536, 764, 388, 730, 776, 1118, 400, 514, 708, 1050, 674, 1244],
      [274, 502, 502, 650, 536, 0, 228, 308, 194, 240, 582, 776, 662, 628, 514, 1050, 708],
      [502, 730, 274, 878, 764, 228, 0, 536, 194, 468, 354, 1004, 890, 856, 514, 1278, 480],
      [194, 354, 810, 502, 388, 308, 536, 0, 342, 388, 730, 468, 354, 320, 662, 742, 856],
      [308, 696, 468, 844, 730, 194, 194, 342, 0, 274, 388, 810, 696, 662, 320, 1084, 514],
      [194, 742, 742, 890, 776, 240, 468, 388, 274, 0, 342, 536, 422, 388, 274, 810, 468],
      [536, 1084, 400, 1232, 1118, 582, 354, 730, 388, 342, 0, 878, 764, 730, 388, 1152, 354],
      [502, 594, 1278, 514, 400, 776, 1004, 468, 810, 536, 878, 0, 114, 308, 650, 274, 844],
      [388, 480, 1164, 628, 514, 662, 890, 354, 696, 422, 764, 114, 0, 194, 536, 388, 730],
      [354, 674, 1130, 822, 708, 628, 856, 320, 662, 388, 730, 308, 194, 0, 342, 422, 536],
      [468, 1016, 788, 1164, 1050, 514, 514, 662, 320, 274, 388, 650, 536, 342, 0, 764, 194],
      [776, 868, 1552, 560, 674, 1050, 1278, 742, 1084, 810, 1152, 274, 388, 422, 764, 0, 798],
      [662, 1210, 754, 1358, 1244, 708, 480, 856, 514, 468, 354, 844, 730, 536, 194, 798, 0],
    ]

N = len(matrix)

pickup_deli = [
        [1, 6],
        [2, 10],
        [4, 3],
        [5, 9],
        [7, 8],
        [15, 11],
        [13, 12],
        [16, 14],
    ]

demands_list = [0] + [1 for _ in range(len(matrix) - 1)]

cap_dict = {1 : 4, 2 : 6, 3 : 2, 4 : 4}

class SingleTour:
    
    def __init__(self):
        self.tour = []
        self.tour_dict = {n+1 : [i, 0] for i, n in enumerate(range(N-1))}
        
    def set_tour(self, external_tour):
        self.tour.extend(external_tour)
    
    def generate_initial_tour(self):
        tours = [n for n in range(1, N)]
        shuffle(tours)
        self.tour.extend(tours)
        return self.tour
    
    def fitness(self):
        distance = 0
        penalty = 0
        cumu_dem = 0
        prev = 0
        vehicle = 1
        
        for idx, city in enumerate(self.tour):
            if cumu_dem + demands_list[city] <= cap_dict[vehicle]:
                distance += matrix[prev][city]
                cumu_dem += demands_list[city]
                prev = city
                self.tour_dict[city][0] = idx
                self.tour_dict[city][1] = vehicle
            else:
                vehicle += 1
                distance += matrix[prev][0]
                cumu_dem = demands_list[city]
                prev = 0
                distance += matrix[prev][city]
                prev = city
                self.tour_dict[city][0] = idx
                self.tour_dict[city][1] = vehicle
        distance += matrix[self.tour[-1]][0]
        
        for p, d in pickup_deli:
            if (self.tour_dict[p][0] > self.tour_dict[d][0] or 
                self.tour_dict[p][1] != self.tour_dict[d][1]):
                penalty += 1000
        
        return distance + penalty
    
    def swap(self, idx1, idx2):
        self.tour[idx1], self.tour[idx2] = self.tour[idx2], self.tour[idx1]
    
    def insertion(self, idx1, idx2):
        if idx1 > idx2:
            idx1, idx2 = idx2, idx1
        new_state = self.tour[:]
        new_state[:idx1] = self.tour[:idx1]
        new_state[idx1] = self.tour[idx2]
        new_state[idx2:] = self.tour[idx2:]
        new_state[idx1 + 1:idx2 + 1] = self.tour[idx1:idx2]
        self.tour = new_state
    
    def inversion(self, idx1, idx2):
        if idx1 > idx2:
            idx1, idx2 = idx2, idx1
        new_state = self.tour[:]
        new_state[idx1:idx2 + 1] = self.tour[idx1:idx2 + 1][::-1]
        self.tour = new_state
    
    def __repr__(self):
        return "-".join(str(e) for e in self.tour)
    
class SimulatedAnnealing:
    
    def __init__(self, t_min, t_max, cooling_rate = 0.999):
        self.t_min = t_min
        self.t_max = t_max
        self.cooling_rate = cooling_rate
        self.actual_state = SingleTour()
        self.next_state, self.best_state = None, None
    
    @staticmethod
    def generate_random_state(actual_state):
        new_state = SingleTour()
        new_state.set_tour(actual_state.tour)
        
        rnd_idx1 = randint(0, N-1)
        rnd_idx2 = randint(0, N-1)
        
        if random() < (1/3):
            new_state.swap(rnd_idx1, rnd_idx2)
        elif random() < (2/3):
            new_state.insertion(rnd_idx1, rnd_idx2)
        else:
            new_state.inversion(rnd_idx1, rnd_idx2)
        
        return new_state
    
    @staticmethod
    def acceptance_probably(actual_energy, new_energy, temp):
        if new_energy < actual_energy:
            return 1
        return np.exp((actual_energy - new_energy) / (0.5*temp)) # 0.5 is beta value
    
    def run(self):
        self.actual_state.generate_initial_tour()
        initial_distance = self.actual_state.fitness()
        print(f"Fitness of randomly generated state : {initial_distance}")
        
        self.best_state = self.actual_state
        t_curr = self.t_max
        count = 0
        
        while t_curr > self.t_min:
            new_state = self.generate_random_state(self.actual_state)
            
            actual_energy = self.actual_state.fitness()
            new_energy = new_state.fitness()
            
            if random() < self.acceptance_probably(actual_energy, new_energy, t_curr):
                self.actual_state = new_state
            if self.actual_state.fitness() < self.best_state.fitness():
                self.best_state = self.actual_state
            
            t_curr *= self.cooling_rate
            count += 1
            if count % 1000 == 0:
                print(self.best_state)
                curr_best = self.best_state.fitness()
                print(f"Current best at Iteration-{count} : {curr_best}")
                print(f"Difference from initial : {round(100*((initial_distance - curr_best) / initial_distance), 3)}")
        print(f"Final solution after Simulated Annealing : {self.best_state.fitness()}")
        print(f"Total iterations : {count}")
        print(self.best_state.tour_dict)

sa_algorithm = SimulatedAnnealing(t_min = 10e-5, 
                                  t_max = 100000, 
                                  cooling_rate = 0.9999)
sa_algorithm.run()


# trial = 0
# trial_sol = [0, 13, 15, 11, 12, 0, 5, 2, 10, 9, 0, 1, 4, 3, 6, 0, 7, 8, 16, 14, 0]
# for i in range(len(trial_sol) - 1):
#     trial += matrix[trial_sol[i]][trial_sol[i+1]]
# print(trial)






tour = [4, 3, 15, 11, 7, 1, 6, 8, 5, 2, 10, 9, 16, 14, 13, 12]
# shuffle(tour)

t = SingleTour()
t.set_tour(tour)
# print(t.inversion(3, 6))

print(t.fitness())
        

"""
7-1-6-8-4-3-15-11-16-14-13-12-5-2-10-9
Current best at Iteration-207000 : 7304
Difference from initial : 60.95
Final solution after Simulated Annealing : 7304
Total iterations : 207223
{1: [1, 1], 2: [13, 4], 3: [5, 2], 4: [4, 2], 5: [12, 4], 6: [2, 1], 7: [0, 1], 8: [3, 1], 9: [15, 4], 10: [14, 4], 11: [7, 2], 12: [11, 3], 13: [10, 3], 14: [9, 3], 15: [6, 2], 16: [8, 3]}

13-15-11-12-7-1-4-3-6-8-5-9-2-10-16-14
Current best at Iteration-207000 : 6688
Difference from initial : 61.643
Final solution after Simulated Annealing : 6688
Total iterations : 207223
{1: [5, 2], 2: [12, 4], 3: [7, 2], 4: [6, 2], 5: [10, 3], 6: [8, 2], 7: [4, 2], 8: [9, 2], 9: [11, 3], 10: [13, 4], 11: [2, 1], 12: [3, 1], 13: [0, 1], 14: [15, 4], 15: [1, 1], 16: [14, 4]}
"""
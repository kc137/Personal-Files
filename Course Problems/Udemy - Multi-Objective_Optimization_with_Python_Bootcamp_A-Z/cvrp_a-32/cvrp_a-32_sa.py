from numpy.random import randint
from random import random, shuffle
from cvrp_a_32_sa_data  import demands as demands_list, coords, matrix, capacity as vehicle_capacity, N

import numpy as np, matplotlib.pyplot as plt

# Below 791 (By just swap method) (Optimum - 777)
# best = "26 - 13 - 21 - 31 - 19 - 17 - 6 - 20 - 5 - 25 - 10 - 15 - 9 - 22 - 29 - 2 - 3 - 23 - 28 - 4 - 11 - 8 - 18 - 16 - 7 - 1 - 12 - 30 - 27 - 24 - 14"

# Below - 789 (By 3-Methods from Paper) (Optimum - 777)
# best = "26-13-17-19-31-21-16-27-24-7-1-12-20-5-25-10-29-15-22-9-8-18-6-3-2-23-28-4-11-14-30"
# best_tour = best.split("-")

# best_tour = [int(city) for city in best_tour]
# tour = best_tour

class SingleTour:
    def __init__(self):
        self.tour = []
    
    def set_tour(self, ext_tour):
        self.tour.extend(ext_tour)
    
    def generate_initial_tour(self):
        tour = [n for n in range(1, N)]
        shuffle(tour)
        self.tour.extend(tour)
        return self.tour

    def get_distance(self):
        distance = 0
        cumu_dem = 0
        prev = 0
        for city in self.tour:
            if cumu_dem + demands_list[city] <= vehicle_capacity:
                distance += matrix[prev][city]
                cumu_dem += demands_list[city]
                prev = city
            else:
                distance += matrix[prev][0]
                cumu_dem = demands_list[city]
                prev = 0
                distance += matrix[prev][city]
                prev = city
        distance += matrix[self.tour[-1]][0]
        return distance
    
    def swap(self, idx1, idx2):
        self.tour[idx1], self.tour[idx2] = self.tour[idx2], self.tour[idx1]
    
    def insertion(self, idx1, idx2):
        if idx1 > idx2:
            idx1, idx2 = idx2, idx1
        new_tours = [0 for _ in range(N)]
        new_tours[:idx1] = self.tour[:idx1]
        new_tours[idx2 + 1:] = self.tour[idx2 + 1:]
        new_tours[idx1] = self.tour[idx2]
        new_tours[idx1 + 1:idx2 + 1] = self.tour[idx1:idx2]
        self.tour = new_tours
    
    def inversion(self, idx1, idx2):
        if idx1 > idx2:
            idx1, idx2 = idx2, idx1
        new_tours = self.tour[:]
        new_tours[idx1:idx2+1] = self.tour[idx1:idx2+1][::-1]
        self.tour = new_tours

    def __repr__(self):
        return "-".join(str(c) for c in self.tour)
        
    
class SimulatedAnnealing:
    
    def __init__(self, t_min, t_max, cooling_rate = 0.999):
        self.t_min = t_min
        self.t_max = t_max
        self.cooling_rate = cooling_rate
        self.actual_state = SingleTour()
        self.best_state, self.new_state = None, None
    
    @staticmethod
    def generate_random_state(state):
        new_state = SingleTour()
        new_state.set_tour(state.tour)
        rnd_idx1, rnd_idx2 = randint(0, N-1), randint(0, N-1)
        while rnd_idx1 == rnd_idx2:
            rnd_idx2 = randint(0, N-1)
        
        if 0 < random() < (1/3):
            new_state.swap(rnd_idx1, rnd_idx2)
        elif 1/3 < random() < (2/3):
            new_state.insertion(rnd_idx1, rnd_idx2)
        else:
            new_state.inversion(rnd_idx1, rnd_idx2)
        
        return new_state
    
    @staticmethod
    def acceptance_probability(actual_energy, new_energy, temp):
        if new_energy < actual_energy:
            return 1
        return np.exp((actual_energy - new_energy) / (0.5*temp))
    
    def run(self):
        self.actual_state.generate_initial_tour()
        initial_distance = self.actual_state.get_distance()
        print(f"Distance before applying Simulated Annealing : {initial_distance}")
        
        self.best_state = self.actual_state
        t_curr = self.t_max
        count = 0
        
        while t_curr > self.t_min:
            new_state = self.generate_random_state(self.actual_state)
            actual_energy = self.actual_state.get_distance()
            new_energy = new_state.get_distance()
            
            if random() < self.acceptance_probability(actual_energy, new_energy, t_curr):
                self.actual_state = new_state
            if self.actual_state.get_distance() < self.best_state.get_distance():
                self.best_state = self.actual_state
            
            t_curr *= self.cooling_rate
            count += 1
            if count % 1000 == 0:
                print(self.best_state)
                print(f"Current best at Iteration-{count} : {self.best_state.get_distance()}")
                print(f"Difference from initial : {round(100*((initial_distance - self.best_state.get_distance()) / initial_distance), 3)}")
        print(f"Final solution after Simulated Annealing : {self.best_state.get_distance()}")
        print(f"Total iterations : {count}")

sa_algorithm = SimulatedAnnealing(t_min = 10e-5, 
                                  t_max = 1000000, 
                                  cooling_rate = 0.9999)
sa_algorithm.run()
                
            
        
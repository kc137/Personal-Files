from numpy.random import randint
from random import random, shuffle
from cvrp_a_32_sa_data  import demands as demands_list, coords, matrix, capacity as vehicle_capacity, N

import numpy as np, matplotlib.pyplot as plt

# best = "26-13-21-31-19-17-6-25-10-15-9-22-29-5-20-30-12-1-7-16-2-3-23-28-4-11-8-18-14-24-27"
# best_tour = best.split("-")

# best_tour = [int(city) for city in best_tour]

# tour = best_tour

tour = [n for n in range(1, N)]
shuffle(tour)

class SingleTour:
    def __init__(self):
        self.tour = []
    
    def set_tour(self, ext_tour):
        self.tour.extend(ext_tour)
    
    def generate_tour(self):
        self.tour.extend(tour)
        return self.tour
    
    def get_tour_size(self):
        return len(self.tour)
    
    def get_distance(self):
        distance = 0
        prev = 0
        c_dem = 0
        
        for loc in self.tour:
            if c_dem + demands_list[loc] <= vehicle_capacity:
                distance += matrix[prev][loc]
                c_dem += demands_list[loc]
                prev = loc
            else:
                distance += matrix[0][prev]
                c_dem = demands_list[loc]
                prev = 0
                distance += matrix[prev][loc]
                prev = loc
        distance += matrix[0][self.tour[-1]]
        return distance

    def swap(self, idx1, idx2):
        self.tour[idx1], self.tour[idx2] = self.tour[idx2], self.tour[idx1]
    
    def __repr__(self):
        return " - ".join(str(e) for e in self.tour) #  + " - " + str(self.tour[0])

class SimulatedAnnealing:
    
    def __init__(self, num_cities, t_min, t_max, cooling_rate = 0.99):
        self.num_cities = num_cities
        self.t_min = t_min
        self.t_max = t_max
        self.cooling_rate = cooling_rate
        self.actual_state = SingleTour()
        self.next_state, self.best_state = None, None
    
    @staticmethod
    def generate_random_state(actual_state):
        new_state = SingleTour()
        # print(f"New State : {new_state}")
        new_state.set_tour(actual_state.tour)
        
        # Swapping two random indexes
        rnd_idx1 = randint(0, new_state.get_tour_size())
        rnd_idx2 = randint(0, new_state.get_tour_size())
        while rnd_idx1 == rnd_idx2:
            rnd_idx2 = randint(0, new_state.get_tour_size())
        
        new_state.swap(rnd_idx1, rnd_idx2)
        
        return new_state
    
    @staticmethod
    def accept_prob(actual_energy, next_energy, temp):
        if next_energy < actual_energy:
            return 1
        return np.exp((actual_energy - next_energy) / temp)
    
    def run(self):
        # self.actual_state.generate_tour(self.num_cities)
        self.actual_state.generate_tour()
        initial_distance = self.actual_state.get_distance()
        print(f"Distance of Initial (Random) Path : {initial_distance}")
        
        self.best_state = self.actual_state
        t_curr = self.t_max
        count = 0
        
        while t_curr > self.t_min:
            # Generate random state based on current one
            new_state = self.generate_random_state(self.actual_state)
            # Calculate the Distances (Energies for analogy of Simulated Annealing)
            actual_energy = self.actual_state.get_distance()
            new_energy = new_state.get_distance()
            
            if random() < self.accept_prob(actual_energy, new_energy, t_curr):
                single_tour = SingleTour()
                single_tour.set_tour(new_state.tour)
                self.actual_state = single_tour
            
            if self.actual_state.get_distance() < self.best_state.get_distance():
                single_tour = SingleTour()
                single_tour.set_tour(self.actual_state.tour)
                self.best_state = single_tour
            
            t_curr *= self.cooling_rate
            count += 1
            if count % 1000 == 0:
                print(self.best_state)
                print(f"Current best at iteration-{count} : {self.best_state.get_distance()}")
                print(f"Difference from initial : {round(100*(initial_distance - self.best_state.get_distance()) / initial_distance, 3)} %")
        
        print(f"The final solution after applying Simulated Annealing : {self.best_state.get_distance()}")
        print(f"Iterations = {count}")
    
            

algorithm = SimulatedAnnealing(17, 10e-5, 1000000, 0.9999)
algorithm.run()


# varc1 = City()
# varc2 = City()
# print(SingleTour.distance(varc1, varc2))

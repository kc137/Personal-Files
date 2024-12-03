from numpy.random import randint
from random import random, shuffle
import numpy as np, matplotlib.pyplot as plt

matrix = [[0, 548, 776, 696, 582, 274, 502, 194, 308, 194, 536, 502, 388, 354, 468, 776, 662],
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
        # fmt: on
    ]
demands_list = [0, 1, 1, 2, 4, 2, 4, 8, 8, 1, 2, 1, 2, 4, 4, 8, 8]
vehicle_capacity = [15]

N = len(matrix)

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
            if c_dem + demands_list[loc] <= vehicle_capacity[0]:
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
    
            

algorithm = SimulatedAnnealing(17, 1e-5, 1000000, 0.999)
algorithm.run()


# varc1 = City()
# varc2 = City()
# print(SingleTour.distance(varc1, varc2))

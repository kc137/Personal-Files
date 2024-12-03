import numpy as np
from numpy.random import randint
from random import random, shuffle
from rc101_25_data import matrix, time_array, demands as demands_list, service_time, capacity
# from rc101_100_data import matrix, time_array, demands as demands_list, service_time, capacity

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
        cumu_dem = 0
        cumu_time = 0
        prev = 0
        for city in self.tour:
            if cumu_time + matrix[prev][city] <= time_array[city][1] and cumu_dem + demands_list[city] <= capacity:
                # print(f"Route - {prev}-{city}")
                distance += matrix[prev][city]
                cumu_dem += demands_list[city]
                if cumu_time < time_array[city][0]:
                    cumu_time = time_array[city][0] + service_time
                else:
                    cumu_time += matrix[prev][city] + service_time
                prev = city
            else:
                # print(f"Route - {prev}-{0}")
                distance += matrix[prev][0]
                cumu_dem = demands_list[city]
                prev = 0
                # print(f"Route - {prev}-{city}")
                distance += matrix[prev][city]
                cumu_time = time_array[city][0] + service_time
                prev = city
        # print(f"Route - {self.tour[-1]}-{0}")
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
        
        if 0 < random() < (1/3):
            new_state.swap(rnd_idx1, rnd_idx2)
        elif random() < (2/3):
            new_state.insertion(rnd_idx1, rnd_idx2)
        else:
            new_state.inversion(rnd_idx1, rnd_idx2)
        
        return new_state
    
    @staticmethod
    def accept_prob(actual_energy, next_energy, temp):
        if next_energy < actual_energy:
            return 1
        return np.exp((actual_energy - next_energy) / (0.5*temp))
    
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

"""
Distance - 481.0 (Obtained between 125000 and 126000) and the best is 461.0
best_so_far = "19 - 22 - 20 - 14 - 12 - 15 - 16 - 17 - 13 - 11 - 9 - 10 - 23 - 21 - 18 - 25 - 24 - 2 - 5 - 7 - 6 - 8 - 3 - 1 - 4"

Distance - 475.0 (Obtained between 125000 and 126000) and the best is 461.0
best_so_far = "23 - 21 - 19 - 18 - 25 - 24 - 12 - 11 - 9 - 10 - 14 - 15 - 16 - 17 - 13 - 22 - 20 - 2 - 5 - 7 - 6 - 8 - 3 - 1 - 4"

Distance - 475.0 (Obtained between 117000 and 118000) and the best is 461.0
best_so_far = "23 - 21 - 19 - 18 - 25 - 24 - 22 - 20 - 12 - 11 - 9 - 10 - 2 - 5 - 7 - 6 - 8 - 3 - 1 - 4 - 14 - 15 - 16 - 17 - 13"

Distance - 462.0 (Obtained between 117000 and 118000) and the best is 461.0
best_so_far = "23 - 21 - 19 - 18 - 25 - 24 - 14 - 12 - 22 - 20 - 11 - 15 - 16 - 9 - 10 - 13 - 17 - 2 - 5 - 7 - 6 - 8 - 3 - 1 - 4"
"""

# varc1 = City()
# varc2 = City()
# print(SingleTour.distance(varc1, varc2))

"""
For 100 Customers
90 - 69 - 88 - 55 - 98 - 12 - 11 - 53 - 61 - 41 - 68 - 82 - 99 - 57 - 20 - 66 - 91 - 80 - 72 - 29 - 31 - 85 - 50 - 93 - 81 - 54 - 96 - 2 - 7 - 8 - 46 - 3 - 1 - 4 - 100 - 70 - 92 - 95 - 62 - 67 - 71 - 94 - 83 - 64 - 51 - 84 - 56 - 65 - 52 - 86 - 87 - 97 - 74 - 58 - 77 - 27 - 28 - 26 - 34 - 14 - 47 - 16 - 15 - 9 - 10 - 39 - 36 - 40 - 38 - 37 - 35 - 73 - 79 - 78 - 17 - 13 - 42 - 44 - 43 - 63 - 76 - 18 - 19 - 48 - 24 - 59 - 75 - 22 - 49 - 89 - 21 - 23 - 25 - 5 - 45 - 6 - 60 - 33 - 30 - 32
Current best at iteration-230000 : 1983.0
Difference from initial : 65.804 %
The final solution after applying Simulated Annealing : 1983.0
Iterations = 230247
"""













































# class VRPTW:
    
#     def __init__(self):
#         self.tour = []
#         # [11, 12, 10, 2, 5, 8, 7, 6, 17, 9, 23, 21, 18, 25, 24, 3, 1, 4, 14, 19, 22, 20, 15, 16, 13]


# def fitness(self, x):
#         distance = 0
#         cumu_dem = 0
#         tardiness = 0
#         cumu_time = 0
#         routes = 0
        
#         for i in range(1, N):
#             if cumu_time + matrix[x[i-1]][x[i]] <= time_array[x[i]][1] and cumu_dem <= capacity:
#                 distance += matrix[x[i-1]][x[i]]
#                 cumu_time += matrix[x[i-1]][x[i]]
#                 if cumu_time < time_array[x[i]][0]:
#                     cumu_time = time_array[x[i]][0] + service_time
#                 else:
#                     cumu_time += service_time
#                 # cumu_dem += demands[x[i]]
#             else:
#                 distance += matrix[x[i-1]][x[0]]
#                 cumu_time = time_array[x[i]][0]
#                 routes += 1
#                 if cumu_time > time_array[x[i]][1]:
#                     # tardiness += cumu_time - time_array[x[i]][1]
#                     cumu_time += service_time
#                 else:
#                     cumu_time += service_time
#                 distance += matrix[x[0]][x[i]]
#                 # cumu_dem = demands[x[i]]
#         distance += matrix[x[-1]][x[0]]
        
#         return (distance, routes)

# vrptw = VRPTW()

# tours = [0, 11, 12, 10, 2, 5, 8, 7, 6, 17, 9, 23, 21, 18, 25, 24, 3, 1, 4, 14, 19, 22, 20, 15, 16, 13]

# print(vrptw.get_distance())

# print(vrptw.fitness(tours))
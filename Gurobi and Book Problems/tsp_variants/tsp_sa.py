from numpy.random import randint
from random import random, shuffle
import numpy as np, matplotlib.pyplot as plt

N = 50

coords = [(32.361538, -86.279118),
 (58.301935, -134.41974),
 (33.448457, -112.073844),
 (34.736009, -92.331122),
 (38.555605, -121.468926),
 (39.7391667, -104.984167),
 (41.767, -72.677),
 (39.161921, -75.526755),
 (30.4518, -84.27277),
 (33.76, -84.39),
 (21.30895, -157.826182),
 (43.613739, -116.237651),
 (39.78325, -89.650373),
 (39.790942, -86.147685),
 (41.590939, -93.620866),
 (39.04, -95.69),
 (38.197274, -84.86311),
 (30.45809, -91.140229),
 (44.323535, -69.765261),
 (38.972945, -76.501157),
 (42.2352, -71.0275),
 (42.7335, -84.5467),
 (44.95, -93.094),
 (32.32, -90.207),
 (38.572954, -92.189283),
 (46.595805, -112.027031),
 (40.809868, -96.675345),
 (39.160949, -119.753877),
 (43.220093, -71.549127),
 (40.221741, -74.756138),
 (35.667231, -105.964575),
 (42.659829, -73.781339),
 (35.771, -78.638),
 (46.813343, -100.779004),
 (39.962245, -83.000647),
 (35.482309, -97.534994),
 (44.931109, -123.029159),
 (40.269789, -76.875613),
 (41.82355, -71.422132),
 (34.0, -81.035),
 (44.367966, -100.336378),
 (36.165, -86.784),
 (30.266667, -97.75),
 (40.7547, -111.892622),
 (44.26639, -72.57194),
 (37.54, -77.46),
 (47.042418, -122.893077),
 (38.349497, -81.633294),
 (43.074722, -89.384444),
 (41.145548, -104.802042)]

class City:
    def __init__(self):
        self.x = round(1000*random())
        self.y = round(1000*random())
    
    def __repr__(self):
        return f"{(self.x, self.y)}"

class Initial_Tour:
    def __init__(self):
        self.tour = []
        self.network_xy = {}
    
    def tour_fill(self, n):
        for i in range(n):
            xy = coords[n]
            self.tour.append(xy)
            self.network_xy[xy] = i+1

    def get_tour(self):
        return self.tour
    
    def get_network(self):
        return self.network_xy

class_initial_tour = Initial_Tour()
class_initial_tour.tour_fill(N-1)

tour = class_initial_tour.get_tour()
network = class_initial_tour.get_network()

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
    
    @staticmethod
    def distance(city1, city2):
        dx = abs(city1.x - city2.x)
        dy = abs(city1.y - city2.y)
        return round(np.sqrt(dx**2 + dy**2))
    
    def get_distance(self):
        tour_distance = 0
        for i in range(len(self.tour)):
            tour_distance += self.distance(self.tour[i % len(self.tour)], 
                                           self.tour[(i+1) % len(self.tour)])
        return tour_distance
    
    def swap(self, idx1, idx2):
        self.tour[idx1], self.tour[idx2] = self.tour[idx2], self.tour[idx1]
    
    def __repr__(self):
        return " - ".join(str(network[e]) for e in self.tour) + " - " + str(network[self.tour[0]])

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
        new_state.set_tour(actual_state.tour)
        
        # Swapping two random indexes
        rnd_idx1 = randint(0, new_state.get_tour_size())
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
            if count % 100 == 0:
                print(self.best_state)
                print(tour)
                print(f"Current best at iteration-{count} : {self.best_state.get_distance()}")
                print(f"Difference from initial : {round(100*(initial_distance - self.best_state.get_distance()) / initial_distance, 3)} %")
        
        print(f"The final solution after applying Simulated Annealing : {self.best_state.get_distance()}")
        print(f"Iterations = {count}")
    
            

algorithm = SimulatedAnnealing(10, 1e-5, 100000, 0.99)
algorithm.run()


# varc1 = City()
# varc2 = City()
# print(SingleTour.distance(varc1, varc2))

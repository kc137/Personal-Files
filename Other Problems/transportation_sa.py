from numpy.random import randint
from random import random, shuffle
from copy import deepcopy
import numpy as np, matplotlib.pyplot as plt

R, C = 3, 4
supply = [300, 400, 500]
demand = [250, 350, 400, 200]
var_matrix = [[1 for _ in range(C)] for _ in range(R)]
cost_matrix = [[3, 1, 7, 4], [2, 6, 5, 9], [8, 3, 3, 2]]

class GenSolution:
    
    def __init__(self):
        self.var_matrix = []
        
    def generate_matrix(self):
        # for r in range(R):
        #     for c in range(C):
        #         var_matrix[r][c] = randint(0, 2)
        self.var_matrix = var_matrix
        return self.var_matrix
    
    def set_matrix(self, ext_matrix):
        self.var_matrix.extend(ext_matrix)
    
    def get_cost(self):
        demand_temp = demand[:]
        supply_temp = supply[:]
        cost = 0
        for r in range(R):
            for c in range(C):
                if var_matrix[r][c]:
                    if supply_temp[r] == 0 and demand_temp[c] == 0:
                        cost += 1000
                    else:
                        to_use = min(supply_temp[r], demand_temp[c])
                        cost += var_matrix[r][c]*cost_matrix[r][c]*to_use
                        demand_temp[c] -= to_use
                        supply_temp[r] -= to_use
        
        for dem in demand_temp:
            if dem:
                cost += 1000
        for sup in supply_temp:
            if sup:
                cost += 1000
        return cost
    
    def __repr__(self):
        return "".join(str(self.var_matrix[r][c]) 
                       for r in range(R) 
                       for c in range(C))
    
    def bit_flip(self):
        for r in range(R):
            for c in range(C):
                if random() < 0.2:
                    if self.var_matrix[r][c]:
                        self.var_matrix[r][c] = 0
                    else:
                        self.var_matrix[r][c] = 1
                    

class SimulatedAnnealing:
    
    def __init__(self, t_min, t_max, cooling_rate):
        self.t_min = t_min
        self.t_max = t_max
        self.cooling_rate = cooling_rate
        self.actual_state = GenSolution()
        self.next_state, self.best_state = None, None
        self.min_best = 10e5
    
    @staticmethod
    def gen_random_state(state):
        new_state = GenSolution()
        new_state.set_matrix(state.var_matrix)
        
        new_state.bit_flip()
        
        return new_state
    
    @staticmethod
    def acceptance_prob(actual_energy, new_energy, t_curr):
        if new_energy < actual_energy:
            return 1
        return (np.exp((actual_energy - new_energy) / (0.5*t_curr)))
    
    def run(self):
        self.actual_state.generate_matrix()
        print(self.actual_state.var_matrix)
        initial_cost = self.actual_state.get_cost()
        print(f"Before SA : {initial_cost} km. is the cost")
        
        self.best_state = deepcopy(self.actual_state)
        best_cost = self.best_state.get_cost()
        if best_cost < self.min_best:
            self.min_best = best_cost
            print(self.min_best, self.best_state)
            self.state_at_min = self.best_state
        t_curr = self.t_max
        count = 0
        
        while t_curr > self.t_min:
            new_state = self.gen_random_state(self.actual_state)
            actual_energy = self.actual_state.get_cost()
            new_energy = new_state.get_cost()
            
            if random() < self.acceptance_prob(actual_energy, new_energy, t_curr):
                self.actual_state = new_state

            if self.actual_state.get_cost() < best_cost:
                self.best_state = self.actual_state
                self.state_at_min = self.best_state
            
            if self.best_state.get_cost() < best_cost:
                best_cost = self.best_state.get_cost()
                self.min_best = best_cost
                self.state_at_min = deepcopy(self.best_state)
            
            t_curr *= self.cooling_rate
            count += 1
            if count % 1000 == 0:
                print(self.best_state, self.state_at_min.var_matrix)
                print(f"Current best at iteration-{count} : {self.best_state.get_cost()} $.")
                print(f"Minimum till now : {self.min_best} $.")
                print(f"Difference from initial : {round(((initial_cost - self.best_state.get_cost()) / initial_cost), 3)}")
        print(f"Final solution after SA : {self.min_best} $.")
        print(f"The best solution : {self.state_at_min}")
        print(f"Total iterations : {count}")
    
    def get_table(self):
        best_matrix = self.state_at_min.var_matrix
        demand_temp = demand[:]
        supply_temp = supply[:]
        res_table = [[0]*C for _ in range(R)]
        
        for r in range(R):
            for c in range(C):
                if best_matrix[r][c]:
                    to_use = min(supply_temp[r], demand_temp[c])
                    demand_temp[c] -= to_use
                    supply_temp[r] -= to_use
                    res_table[r][c] = to_use
        return res_table
        

sa_algo = SimulatedAnnealing(t_min = 10e-5, 
                             t_max = 10e4, 
                             cooling_rate = 0.999)
sa_algo.run()

transportation_table = sa_algo.get_table()
print(transportation_table)

"""
Over
R, C = 3, 4
supply = [300, 400, 500]
demand = [250, 350, 400, 200]
# var_matrix = [[1 for _ in range(C)] for _ in range(R)]
var_matrix = [[1, 1, 0, 0], [0, 1, 1, 0], [0, 0, 1, 1]]

cost_matrix = [[3, 1, 7, 4], [2, 6, 5, 9], [8, 3, 3, 2]]
"""

"""
To Try
R, C = 3, 4
supply = [50, 50, 50]
demand = [45, 15, 25, 20]
var_matrix = [[1 for _ in range(C)] for _ in range(R)]
cost_matrix = [[8, 10, 6, 3], [9, 15, 8, 6], [5, 12, 5, 7]]
"""

"""
To Try
R, C = 3, 4
supply = [50, 50, 50]
demand = [45, 15, 40, 50]
var_matrix = [[1 for _ in range(C)] for _ in range(R)]
cost_matrix = [[8, 10, 6, 3], [9, 15, 8, 6], [5, 12, 5, 7]]
"""






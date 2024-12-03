from numpy.random import randint
from random import random, shuffle
from copy import deepcopy
import numpy as np, matplotlib.pyplot as plt

# R, C = 3, 4
# supply = [300, 400, 500]
# demand = [250, 350, 400, 200]
# var_matrix = [[1 for _ in range(C)] for _ in range(R)]
# cost_matrix = [[3, 1, 7, 4], [2, 6, 5, 9], [8, 3, 3, 2]]

R, C = 3, 4
supply = [50, 50, 50]
demand = [45, 15, 40, 50]
var_matrix = [[1 for _ in range(C)] for _ in range(R)]
# var_matrix = [[0, 1, 0, 1], [0, 0, 1, 1], [1, 0, 1, 0]]
var_matrix = [[0, 1, 1, 1], [1, 0, 0, 0], [1, 0, 0, 0]]
cost_matrix = [[8, 10, 6, 3], [9, 15, 8, 6], [5, 12, 5, 7]]

class GenSolution:
    
    def __init__(self):
        self.var_matrix = []
        self.state_elements = []
        
    def generate_matrix(self):
        for r in range(R):
            for c in range(C):
                var_matrix[r][c] = randint(0, 2)
        self.var_matrix = var_matrix
        return self.var_matrix
    
    def set_matrix(self, ext_matrix):
        self.var_matrix.extend(ext_matrix)
    
    def get_cost(self):
        demand_temp = demand[:]
        supply_temp = supply[:]
        cost = 0
        
        elements = list(range(R*C))
        shuffle(elements)
        
        self.state_elements = elements
        
        for i in elements:
            c = i % C
            r = i // C if i % C else i // C - 1
            if self.var_matrix[r][c]:
                if supply_temp[r] == 0 or demand_temp[c] == 0:
                    cost += 1000
                else:
                    to_use = min(supply_temp[r], demand_temp[c])
                    cost += self.var_matrix[r][c]*cost_matrix[r][c]*to_use
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
        self.best_elements = []
    
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
        print(f"Before SA : ${initial_cost} is the cost")
        
        self.best_state = deepcopy(self.actual_state)
        new_best_cost = best_cost = initial_cost
        if best_cost < self.min_best:
            self.min_best = best_cost
            print(self.min_best, self.best_state)
            self.state_at_min = self.best_state
            self.best_elements = self.best_state.state_elements
        t_curr = self.t_max
        count = 0
        
        while t_curr > self.t_min:
            new_state = self.gen_random_state(self.actual_state)
            actual_energy = self.actual_state.get_cost()
            new_energy = new_state.get_cost()
            
            if random() < self.acceptance_prob(actual_energy, new_energy, t_curr):
                self.actual_state = new_state

            actual_cost = self.actual_state.get_cost()
            
            if actual_cost < best_cost:
                new_best_cost = actual_cost
                self.best_state = self.actual_state
                self.state_at_min = deepcopy(self.best_state)
                self.best_elements = deepcopy(self.actual_state.state_elements)
            
            if new_best_cost < best_cost:
                best_cost = new_best_cost
                self.min_best = new_best_cost
                self.state_at_min = deepcopy(self.best_state)
                self.best_elements = self.state_at_min.state_elements
            
            t_curr *= self.cooling_rate
            count += 1
            if count % 1000 == 0:
                print(self.best_state, self.state_at_min.var_matrix)
                print(f"Current best at iteration-{count} : {self.best_state.get_cost()} $.")
                print(f"Minimum till now : {self.min_best} $.")
                # print(f"Difference from initial : {round(((initial_cost - self.best_state.get_cost()) / initial_cost), 3)}")
        print(f"Final solution after SA : ${self.min_best}.")
        print(f"The best solution : {self.state_at_min}")
        print(f"Total iterations : {count}")
    
    def get_table(self):
        best_matrix = self.state_at_min.var_matrix
        demand_temp = demand[:]
        supply_temp = supply[:]
        res_table = [[0]*C for _ in range(R)]
        
        for i in self.best_elements:
            r = i // C if i % C else i // C - 1
            c = i % C
            if best_matrix[r][c]:
                to_use = min(supply_temp[r], demand_temp[c])
                demand_temp[c] -= to_use
                supply_temp[r] -= to_use
                res_table[r][c] = to_use
        return res_table, self.best_elements
        

sa_algo = SimulatedAnnealing(t_min = 10e-5, 
                             t_max = 10e4, 
                             cooling_rate = 0.9995)
sa_algo.run()

transportation_table, elements = sa_algo.get_table()

print(transportation_table)
print(elements)


"""
110001110001 [[0, 1, 0, 1], [0, 0, 1, 1], [1, 0, 1, 0]]
Current best at iteration-41000 : 2230 $.
Minimum till now : 875 $.
Final solution after SA : $875.
The best solution : 010100111010
Total iterations : 41437
[[0, 15, 0, 35], [0, 0, 40, 10], [45, 0, 0, 0]]
"""

"""
Current best at iteration-41000 : 4780 $.
Minimum till now : 875 $.
Final solution after SA : $875.
The best solution : 010100111010
Total iterations : 41437
[0, 0, 0, 0] [0, 0, 0]
[0, 0, 0, 0] [0, 0, 0]
[[0, 15, 0, 35], [0, 0, 35, 15], [45, 0, 5, 0]]
[1, 0, 5, 11, 8, 10, 3, 4, 6, 2, 9, 7]
"""
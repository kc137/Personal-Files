import numpy as np
from numpy.random import randint
from random import random, shuffle

N = 9+1
J, M = 3, 3

times_dict = {n : [[0, 0] for _ in range(J)] for n in range(1, M+1)}

data = [
        [3, 3, 3], 
        [2, 4, 3], 
        [2, 3, 1]
        ]

[5, 3, 7, 8, 4, 1, 6, 2, 9]

"""
Optimal (My assumption) : [1, 2, 3, 6, 4, 5, 8, 7, 9]

    M1  M2  M3
J1  3   3   3
J2  2   4   3
J3  2   3   1

    M1   M2   M3    M1  M2  M3
J1  O11  O12  O13   1   2   3
J2  O21  O22  O23   4   5   6
J3  O31  O32  O33   7   8   9

    M1   M2   M3 
    O22  O32  O23
    O13  O21  O12
    O31  O11  O33
"""

class Sequence:
    
    def __init__(self):
        self.sequence = []
        self.jobs_dict = {n+1 : 0 for n in range(J-1)}
        self.machines_dict = {n+1 : 0 for n in range(M-1)}
        
    def set_sequence(self, external_sequence):
        self.sequence.extend(external_sequence)
    
    def generate_initial_sequence(self):
        sequence = [n for n in range(1, N)]
        shuffle(sequence)
        self.sequence.extend(sequence)
        return self.sequence
    
    def fitness(self):
        makespan = 0
        j, m = 1, 1
        # for i, op in enumerate(self.sequence):
            
        return
    
    def swap(self, idx1, idx2):
        self.sequence[idx1], self.sequence[idx2] = self.sequence[idx2], self.sequence[idx1]
    
    def insertion(self, idx1, idx2):
        if idx1 > idx2:
            idx1, idx2 = idx2, idx1
        new_state = self.sequence[:]
        new_state[:idx1] = self.sequence[:idx1]
        new_state[idx1] = self.sequence[idx2]
        new_state[idx2:] = self.sequence[idx2:]
        new_state[idx1 + 1:idx2 + 1] = self.sequence[idx1:idx2]
        self.sequence = new_state
    
    def inversion(self, idx1, idx2):
        if idx1 > idx2:
            idx1, idx2 = idx2, idx1
        new_state = self.sequence[:]
        new_state[idx1:idx2 + 1] = self.sequence[idx1:idx2 + 1][::-1]
        self.sequence = new_state
    
    def __repr__(self):
        return "-".join(str(e) for e in self.sequence)
    
class SimulatedAnnealing:
    
    def __init__(self, t_min, t_max, cooling_rate = 0.999):
        self.t_min = t_min
        self.t_max = t_max
        self.cooling_rate = cooling_rate
        self.actual_state = Sequence()
        self.next_state, self.best_state = None, None
    
    @staticmethod
    def generate_random_state(actual_state):
        new_state = Sequence()
        new_state.set_sequence(actual_state.sequence)
        
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
        self.actual_state.generate_initial_sequence()
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
        print(self.best_state.sequence_dict)

# sa_algorithm = SimulatedAnnealing(t_min = 10e-5, 
#                                   t_max = 100000, 
#                                   cooling_rate = 0.9999)
# sa_algorithm.run()




sequence = [4, 3, 15, 11, 7, 1, 6, 8, 5, 2, 10, 9, 16, 14, 13, 12]
# shuffle(sequence)

t = Sequence()
t.set_sequence(sequence)
# print(t.inversion(3, 6))

print(t.fitness())
        


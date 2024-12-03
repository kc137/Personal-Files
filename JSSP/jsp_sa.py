import pandas as pd, numpy as np, plotly.figure_factory as ff
from numpy.random import randint
from random import random, shuffle
from copy import deepcopy

data = """
        2	1	0	3	1	6	3	7	5	3	4	6
        1	8	2	5	4	10	5	10	0	10	3	4
        2	5	3	4	5	8	0	9	1	1	4	7
        1	5	0	5	2	5	3	3	4	8	5	9
        2	9	1	3	4	5	5	4	0	3	3	1
        1	3	3	3	5	9	0	10	4	4	2	1
        """

data = data.split()

machine_sequence = [[]]
processing_times = [[]]

data_len = len(data)

for i, num in enumerate(data):
    if i % 2:
        processing_times[-1].append(int(num))
        if (i + 1) % 12 == 0 and i != data_len - 1:
            processing_times.append([])
    else:
        machine_sequence[-1].append(int(num) + 1)
        if len(machine_sequence[-1]) == 6 and i != data_len - 2:
            machine_sequence.append([])
    
NJ, NM = len(processing_times), len(machine_sequence[0])

class Sequence:
    
    def __init__(self):
        self.sequence = []
    
    def gen_initial_seq(self):
        seq = [n for n in range(1, NJ*NM + 1)]
        for i in range(len(seq)):
            seq[i] = seq[i] % NJ if seq[i] % NJ else NJ
        shuffle(seq)
        self.sequence.extend(seq)
        return self.sequence
    
    def set_seq(self, ext_seq):
        self.sequence.extend(ext_seq)
    
    def fitness(self):
        keys = {k : 0 for k in range(1, NJ + 1)}
        j_time = {j : 0 for j in keys}
        m_time = {m : 0 for m in range(1, NM + 1)}
        
        for j in self.sequence:
            processing_time = processing_times[j-1][keys[j]]
            curr_m = machine_sequence[j-1][keys[j]]
            
            j_time[j] += processing_time
            m_time[curr_m] += processing_time
            
            to_add = max(j_time[j], m_time[curr_m])
            
            j_time[j], m_time[curr_m] = to_add, to_add
            
            keys[j] += 1
        
        makespan = max(j_time.values())
        
        return makespan
    
    def swap(self, idx1, idx2):
        self.sequence[idx1], self.sequence[idx2] = self.sequence[idx2], self.sequence[idx1]
        
    def insertion(self, idx1, idx2):
        if idx1 > idx2:
            idx1, idx2 = idx2, idx1
        new_seq = self.sequence[:]
        new_seq[idx1] = self.sequence[idx2]
        new_seq[idx1 + 1:idx2 + 1] = self.sequence[idx1:idx2]
        self.sequence = new_seq
        
    
    def inversion(self, idx1, idx2):
        if idx1 > idx2:
            idx1, idx2 = idx2, idx1
        new_seq = self.sequence[:]
        new_seq[idx1:idx2 + 1] = self.sequence[idx1:idx2 + 1][::-1]
        self.sequence = new_seq
    
    def __repr__(self):
        return "-".join(str(j) for j in self.sequence)

class SimulatedAnnealing:
    
    def __init__(self, t_min, t_max, cooling_rate):
        self.t_min = t_min
        self.t_max = t_max
        self.cooling_rate = cooling_rate
        self.actual_state = Sequence()
        # self.new_state = self.best_state = None
        self.new_state, self.best_state = None, None
    
    @staticmethod
    def gen_random_state(actual_state):
        new_state = Sequence()
        new_state.set_seq(actual_state.sequence)
        
        rnd_idx1, rnd_idx2 = randint(0, NJ*NM), randint(0, NJ*NM)
        while rnd_idx1 == rnd_idx2:
            rnd_idx2 = randint(0, NJ*NM)
        rnd_val = random()
        
        if rnd_val < (1/3):
            new_state.swap(rnd_idx1, rnd_idx2)
        elif rnd_val < (2/3):
            new_state.insertion(rnd_idx1, rnd_idx2)
        else:
            new_state.inversion(rnd_idx1, rnd_idx2)
        
        return new_state
    
    @staticmethod
    def acceptance_probability(actual_energy, new_energy, temp):
        if new_energy < actual_energy:
            return 1
        return np.exp((actual_energy - new_energy)/(0.5*temp))
    
    def get_best_state(self):
        state_str = str(self.best_state)
        state_str = state_str.split("-")
        state_str = [int(j) for j in state_str]
        return state_str
    
    def run(self):
        
        self.actual_state.gen_initial_seq()
        initial_energy = self.actual_state.fitness()
        
        print(f"The initial solution before SA-Algo : {initial_energy} min.")
        
        self.best_state = self.actual_state
        t_curr = self.t_max
        count = 0
        
        while t_curr > self.t_min:
            new_state = self.gen_random_state(self.actual_state)
            
            new_energy = new_state.fitness()
            actual_energy = self.actual_state.fitness()
            best_energy = self.best_state.fitness()
            
            if random() < self.acceptance_probability(actual_energy, new_energy, t_curr):
                self.actual_state = deepcopy(new_state)
                actual_energy = self.actual_state.fitness()
            if actual_energy < best_energy:
                self.best_state = deepcopy(self.actual_state)
                best_energy = self.best_state.fitness()
            t_curr *= self.cooling_rate
            count += 1
            
            if count % 1000 == 0:
                print("Best sequence till now : ")
                print(self.best_state)
                print(f"Current best at iteration-{count} : {best_energy} min.")
        
        print(f"Final solution after SA-Algorithm : {best_energy} min.")
        print(f"Total iteration : {count}.")
    
    
sa_algo = SimulatedAnnealing(t_min = 10e-5, 
                             t_max = 10e5, 
                             cooling_rate = 0.999)
sa_algo.run()
            
                
        
        
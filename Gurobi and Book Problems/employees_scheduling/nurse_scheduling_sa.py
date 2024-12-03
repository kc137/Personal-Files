import numpy as np
from numpy.random import randint, random, shuffle

N, S, D = 12, 3, 7

nurse_shift_allocation = np.zeros(shape = [N, D*S], dtype = int)
not_pre_list = [[2], [1, 3], [1, 2], [], [1], [2], [], [1, 2], [1, 3], [3], [1], [2, 3]]
nurse_per_shift_list = [[3, 4], [3, 4], [2, 3]]

for r in range(N):
    for c in range(len(nurse_shift_allocation[0])):
        nurse_shift_allocation[r][c] = randint(0, 1+1)

initial_solution = nurse_shift_allocation[:]
R, C = len(initial_solution), len(initial_solution[0])

initial = [
    [0 for _ in range(S*D - (N//2))] + [1 for _ in range(N//2)] 
    for _ in range(N)
    ]

[shuffle(ini) for ini in initial]

"""
Random Bit Flipping should be tried for the Solution
"""

class Schedule:
    
    def __init__(self):
        self.nsa = np.zeros(shape = [N, D*S], dtype = int)
        self.av, self.bv, self.cv = 0, 0, 0
    
    def gen_random_state(self):
        for r in range(N):
            for c in range(len(self.nsa[0])):
                # self.nsa[r][c] = randint(0, 1+1)
                self.nsa[r][c] = randint(0, 1)
    
    def set_schedule(self, actual_state):
        self.nsa = actual_state
    
    def fitness(self):
        week_shifts_violations = 0
        nurses_shifts_violations = 0
        shift_preference_violations = 0
        
        nurses_per_shift = {c : 0 for c in range(C)}
        week_shifts = {r : 0 for r in range(R)}
        nurse_shift_count = {r : {s : 0 for s in range(S)} for r in range(R)}
        
        for r in range(R):
            week_shifts_in_row = 0
            for c in range(C):
                if self.nsa[r][c] == 1:
                    week_shifts_in_row += 1
                    nurses_per_shift[c] += 1
                    nurse_shift_count[r][c % 3] += 1
            week_shifts[r] = week_shifts_in_row
        # print(week_shifts)
        for n in week_shifts:
            if week_shifts[n] > 5:
                week_shifts_violations += 10
        # print(nurses_per_shift)
        for s in nurses_per_shift:
            if (nurses_per_shift[s] < nurse_per_shift_list[s % S][0] or 
                nurses_per_shift[s] > nurse_per_shift_list[s % S][1]):
                nurses_shifts_violations += 10
        # print(nurse_shift_count)
        for n in nurse_shift_count:
            curr_shift = nurse_shift_count[n]
            for s in not_pre_list[n]:
                if curr_shift[s-1]:
                    shift_preference_violations += 10
        self.av, self.bv, self.cv = week_shifts_violations, nurses_shifts_violations, shift_preference_violations
        # return self.av + self.bv + self.cv
        return self.av + self.bv
    
    def bit_flip(self):
        for r in range(R):
            for c in range(C):
                curr_val = self.nsa[r][c]
                if random() <= 0.1:
                     self.nsa[r][c] = 0 if curr_val else 1
    
    def __repr__(self):
        return f"week_shifts_violations = {self.av}, \n"\
            f"nurses_shifts_violations = {self.bv}\n"\
            f"shift_preference_violations = {self.cv}"
            
class SimulatedAnnealing:
    
    def __init__(self, t_max, t_min, cooling_rate):
        self.t_max = t_max
        self.t_min = t_min
        self.cooling_rate = cooling_rate
        self.actual_state = Schedule()
        print(self.actual_state)
        self.next_state, self.best_state = None, None
        
    @staticmethod
    def generate_random_state(actual_state):
        new_state = Schedule()
        new_state.set_schedule(actual_state.nsa)
        new_state.bit_flip()
        return new_state
    
    @staticmethod
    def acceptance_probalbility(actual_energy, next_energy, temp):
        if next_energy < actual_energy:
            return 1
        return np.exp((actual_energy - next_energy) / (0.5*temp))
    
    def run(self):
        self.actual_state.gen_random_state()
        # print(self.actual_state.nsa)
        total_violations = self.actual_state.fitness()
        print(f"The total violations before SA Algorithm : {total_violations}")
        
        self.best_state = self.actual_state
        t_curr = self.t_max
        count = 0
        
        while t_curr > self.t_min:
            new_state = self.generate_random_state(self.actual_state)
            actual_energy = self.actual_state.fitness()
            new_energy = new_state.fitness()
            
            if random() < self.acceptance_probalbility(actual_energy, new_energy, t_curr):
                self.actual_state = new_state
            if self.actual_state.fitness() < self.best_state.fitness():
                self.best_state = self.actual_state
            
            t_curr *= self.cooling_rate
            count += 1
            if count % 1000 == 0:
                print(self.best_state)
                print(f"Current best at Iteration-{count} : {self.best_state.fitness()}")
                diff = round(100*((total_violations - self.best_state.fitness()) / total_violations), 3)
                print(f"Difference from initial : {diff}")
        print(f"Final solution after Simulated Annealing : {self.best_state.fitness()}")
        print(f"Total iterations : {count}")

sa_algorithm = SimulatedAnnealing(t_max = 10e5, 
                                  t_min = 10e-4, 
                                  cooling_rate = 0.9993)
sa_algorithm.run()
            

# sch = Schedule()
# print(sch.nsa)
# sch.gen_random_state()
# print(sch.nsa)



















# def fitness(schedule):
#     week_shifts_violations = 0
#     nurses_shifts_violations = 0
#     shift_preference_violations = 0
    
#     nurses_per_shift = {c : 0 for c in range(C)}
#     week_shifts = {r : 0 for r in range(R)}
#     nurse_shift_count = {r : {s : 0 for s in range(S)} for r in range(R)}
    
#     for r in range(R):
#         week_shifts_in_row = 0
#         for c in range(C):
#             if schedule[r][c] == 1:
#                 week_shifts_in_row += 1
#                 nurses_per_shift[c] += 1
#                 nurse_shift_count[r][c % 3] += 1
#         week_shifts[r] = week_shifts_in_row
#     # print(week_shifts)
#     for n in week_shifts:
#         if week_shifts[n] > 5:
#             week_shifts_violations += 10
#     # print(nurses_per_shift)
#     for s in nurses_per_shift:
#         if (nurses_per_shift[s] < nurse_per_shift_list[s % S][0] or 
#             nurses_per_shift[s] > nurse_per_shift_list[s % S][1]):
#             nurses_shifts_violations += 10
#     # print(nurse_shift_count)
#     for n in nurse_shift_count:
#         curr_shift = nurse_shift_count[n]
#         for s in not_pre_list[n]:
#             if curr_shift[s-1]:
#                 shift_preference_violations += 10
    
#     return week_shifts_violations, nurses_shifts_violations, shift_preference_violations

# print(fitness(nurse_shift_allocation))

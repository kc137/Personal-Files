import random, numpy as np
from copy import deepcopy

seed = random.randint(0, 100)
random.seed(seed)


nurses = 12
days = 7
shifts = 3
max_shifts_per_week = 5

N = nurses*days*shifts

nurse_req = [[3, 4], [3, 4], [2, 3]]

shift_pref = [[1, 0, 1], [0, 1, 0], [0, 0, 1], [1, 1, 1], 
              [0, 1, 1], [1, 0, 1], [1, 1, 1], [0, 0, 1], 
              [0, 1, 0], [1, 1, 0], [0, 1, 1], [1, 0, 0]]

flip_bit_prob = 0.03

class Individual:
    
    def __init__(self):
        self.solution = [random.randint(0, 1) for _ in range(N)]
    
    def update_solution(self, new_sol):
        self.solution = deepcopy(new_sol)
    
    def staff_violations(self):
        indv = self.solution
        violations_s1, violations_s2, violations_s3 = 0, 0, 0
        for s in range(0, shifts*days, shifts):
            staff_s1 = sum(indv[s + i] for i in range(0, N, shifts*days))
            staff_s2 = sum(indv[s + i] for i in range(1, N, shifts*days))
            staff_s3 = sum(indv[s + i] for i in range(2, N, shifts*days))
        
            if staff_s1 < nurse_req[0][0] or staff_s1 > nurse_req[0][1]:
                violations_s1 += 10
            if staff_s2 < nurse_req[1][0] or staff_s2 > nurse_req[1][1]:
                violations_s2 += 10
            if staff_s3 < nurse_req[2][0] or staff_s3 > nurse_req[2][1]:
                violations_s3 += 10
            
        return violations_s1 + violations_s2 + violations_s3
    
    def shift_violations(self):
        indv = self.solution
        
        violations = 0
        n = shifts*days
        
        for i in range(0, N, shifts):
            staff_s1, staff_s2, staff_s3 = indv[i], indv[i+1], indv[i+2]
            
            if shift_pref[i // n][0] == 0 and shift_pref[i // n][0] != staff_s1:
                violations += 10
            if shift_pref[i // n][1] == 0 and shift_pref[i // n][1] != staff_s2:
                violations += 10
            if shift_pref[i // n][2] == 0 and shift_pref[i // n][2] != staff_s3:
                violations += 10
        
        return violations
    
    def consecutive_violations(self):
        indv = self.solution
        violations = 0
        
        for i in range(0, N, shifts):
            total_staff = indv[i:i + shifts]
            
            for j in range(shifts - 1):
                if total_staff[j] and total_staff[j] == total_staff[j+1]:
                    violations += 10
            
        return violations
    
    def week_violations(self):
        indv = self.solution
        violations = 0
        
        for i in range(0, N, shifts*days):
            nurse_shifts = sum(indv[i:i + shifts*days])
            if nurse_shifts > max_shifts_per_week:
                violations += 10
        return violations
    
    def obj_fn(self):
        total_violations = (self.staff_violations() 
                            + self.shift_violations() 
                            + self.consecutive_violations() 
                            + self.week_violations())
        return total_violations
    
    def flipbit(self):
        for i in range(N):
            if random.random() <= flip_bit_prob:
                if self.solution[i]:
                    self.solution[i] = 0
                else:
                    self.solution[i] = 1
        return
    
    def insertion(self):
        indv = deepcopy(self.solution)
        rnd_idx1, rnd_idx2 = random.randint(1, N-2), random.randint(1, N-2)
        
        if rnd_idx1 == rnd_idx2:
            while rnd_idx1 == rnd_idx2:
                rnd_idx2 = random.randint(1, N-2)
        if rnd_idx1 > rnd_idx2:
            rnd_idx1, rnd_idx2 = rnd_idx2, rnd_idx1
        
        indv[rnd_idx1] = self.solution[rnd_idx2]
        indv[rnd_idx1 + 1:rnd_idx2 + 1] = self.solution[rnd_idx1:rnd_idx2]
        
        self.solution = indv
        
        return self.solution
    
    def inversion(self):
        indv = deepcopy(self.solution)
        rnd_idx1, rnd_idx2 = random.randint(1, N-2), random.randint(1, N-2)
        
        if rnd_idx1 == rnd_idx2:
            while rnd_idx1 == rnd_idx2:
                rnd_idx2 = random.randint(1, N-2)
        if rnd_idx1 > rnd_idx2:
            rnd_idx1, rnd_idx2 = rnd_idx2, rnd_idx1
        
        indv[rnd_idx1:rnd_idx2 + 1] = self.solution[rnd_idx1:rnd_idx2 + 1][::-1]
        
        self.solution = indv
        
        return self.solution
    

class SimulatedAnnealing:
    
    def __init__(self, t_min, t_max, cooling_rate):
        self.t_min = t_min
        self.t_max = t_max
        self.cooling_rate = cooling_rate
        self.actual_state = None
        self.best_state = None
        self.best_value = float("inf")
        
    @staticmethod    
    def generate_random_state(actual_state):
        new_state = deepcopy(actual_state)
        
        if random.random() < (1/3):
            new_state.inversion()
        elif random.random() < (2/3):
            new_state.flipbit()
        else:
            new_state.insertion()
        
        return new_state
    
    @staticmethod
    def acceptance_probability(actual_energy, new_energy, t_curr):
        if new_energy < actual_energy:
            return 1
        return np.exp((actual_energy - new_energy) / 0.8*(t_curr))
    
    def run(self):
        self.actual_state = Individual()
        self.best_value = self.actual_state.obj_fn()
        initial_value = self.best_value
        self.best_state = deepcopy(self.actual_state)
        best_iteration = 0
        
        t_curr = self.t_max
        iteration = 0
        
        while t_curr > self.t_min:
            
            self.new_state = self.generate_random_state(self.actual_state)
            actual_energy = self.actual_state.obj_fn()
            new_energy = self.new_state.obj_fn()
            
            if random.random() < self.acceptance_probability(actual_energy, new_energy, t_curr):
                self.actual_state = deepcopy(self.new_state)
            
            actual_energy = self.actual_state.obj_fn()
            
            if actual_energy < self.best_value:
                self.best_state = deepcopy(self.actual_state)
                self.best_value = actual_energy
                best_iteration = iteration
            
            t_curr *= self.cooling_rate
            iteration += 1
            
            if iteration % 1000 == 0:
                print(f"Solution at Iteration-{iteration} : {actual_energy}")
                print(f"Best solution till now : {self.best_value} (At Iteration-{best_iteration})")
                diff = round(100*(abs(initial_value - self.best_value) / self.best_value), 3)
                print(f"Difference from initial : {diff}%")
        
        print(f"Final Solution after SA : {self.best_value}")
        print(f"Best individual : {self.best_state.solution}")
        print(f"Best solution obtained at : {best_iteration} with Seed-{seed}")
        print(f"Total iterations-{iteration}")

sa_algo = SimulatedAnnealing(t_min = 10e0, 
                             t_max = 10e9, 
                             cooling_rate = 0.9992)
sa_algo.run()


"""
Best solution till now : 40 (At Iteration-18007)
Difference from initial : 3075.0%
Final Solution after SA : 40
Best individual : [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1, 0, 0, 1, 0, 1, 1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0]
Best solution obtained at : 18007 with Seed-92
Total iterations-25894

Best solution till now : 40 (At Iteration-21633)
Difference from initial : 3225.0%
Final Solution after SA : 40
Best individual : [0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 1, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 1, 1, 0, 0, 1, 0, 1, 0, 1, 0, 1, 0, 0, 0, 0, 1, 1, 0, 1, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 1, 0, 1, 1, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
Best solution obtained at : 21633 with Seed-46
Total iterations-25894

Best solution till now : 50 (At Iteration-15200)
Difference from initial : 2300.0%
Final Solution after SA : 50
Best individual : [1, 0, 1, 0, 0, 1, 1, 0, 1, 1, 0, 0, 0, 0, 1, 1, 0, 1, 1, 0, 1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 1, 0, 0, 1, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 1, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0]
Best solution obtained at : 15200 with Seed-70
Total iterations-20713

"""







"""
Wrong Function

Best solution till now : 0 (At Iteration-21970)
Difference from initial : 100.0
Final Solution after SA : 0
Best individual : [0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0]
Best solution obtained at : 21970 with Seed-40
Total iterations-46043

Best solution till now : 20 (At Iteration-21728)
Difference from initial : 97.403
Final Solution after SA : 20
Best individual : [0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 1, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 1, 0, 1, 0, 0, 0, 1, 0, 1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 1, 1, 0, 1, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0]
Best solution obtained at : 21728 with Seed-9
Total iterations-36833
"""

            
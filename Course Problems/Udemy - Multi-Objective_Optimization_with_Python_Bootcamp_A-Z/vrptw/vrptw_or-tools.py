import numpy as np
from pymoo.core.problem import ElementwiseProblem
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.operators.sampling.rnd import PermutationRandomSampling
from pymoo.operators.crossover.ox import OrderCrossover
from pymoo.operators.repair.rounding import RoundingRepair
from pymoo.operators.mutation.inversion import InversionMutation
from pymoo.termination import get_termination
from pymoo.optimize import minimize



matrix = np.array([
        [0, 6, 9, 8, 7, 3, 6, 2, 3, 2, 6, 6, 4, 4, 5, 9, 7],
        [6, 0, 8, 3, 2, 6, 8, 4, 8, 8, 13, 7, 5, 8, 12, 10, 14],
        [9, 8, 0, 11, 10, 6, 3, 9, 5, 8, 4, 15, 14, 13, 9, 18, 9],
        [8, 3, 11, 0, 1, 7, 10, 6, 10, 10, 14, 6, 7, 9, 14, 6, 16],
        [7, 2, 10, 1, 0, 6, 9, 4, 8, 9, 13, 4, 6, 8, 12, 8, 14],
        [3, 6, 6, 7, 6, 0, 2, 3, 2, 2, 7, 9, 7, 7, 6, 12, 8],
        [6, 8, 3, 10, 9, 2, 0, 6, 2, 5, 4, 12, 10, 10, 6, 15, 5],
        [2, 4, 9, 6, 4, 3, 6, 0, 4, 4, 8, 5, 4, 3, 7, 8, 10],
        [3, 8, 5, 10, 8, 2, 2, 4, 0, 3, 4, 9, 8, 7, 3, 13, 6],
        [2, 8, 8, 10, 9, 2, 5, 4, 3, 0, 4, 6, 5, 4, 3, 9, 5],
        [6, 13, 4, 14, 13, 7, 4, 8, 4, 4, 0, 10, 9, 8, 4, 13, 4],
        [6, 7, 15, 6, 4, 9, 12, 5, 9, 6, 10, 0, 1, 3, 7, 3, 10],
        [4, 5, 14, 7, 6, 7, 10, 4, 8, 5, 9, 1, 0, 2, 6, 4, 8],
        [4, 8, 13, 9, 8, 7, 10, 3, 7, 4, 8, 3, 2, 0, 4, 5, 6],
        [5, 12, 9, 14, 12, 6, 6, 7, 3, 3, 4, 7, 6, 4, 0, 9, 2],
        [9, 10, 18, 6, 8, 12, 15, 8, 13, 9, 13, 3, 4, 5, 9, 0, 9],
        [7, 14, 9, 16, 14, 8, 5, 10, 6, 5, 4, 10, 8, 6, 2, 9, 0],
    ])

time_windows = np.array([
        (0, 5),  # depot
        (7, 12),  # 1
        (10, 15),  # 2
        (16, 18),  # 3
        (10, 13),  # 4
        (0, 5),  # 5
        (5, 10),  # 6
        (0, 4),  # 7
        (5, 10),  # 8
        (0, 3),  # 9
        (10, 16),  # 10
        (10, 15),  # 11
        (0, 5),  # 12
        (5, 10),  # 13
        (7, 8),  # 14
        (10, 15),  # 15
        (11, 15),  # 16
    ])

N = len(matrix)

class VRPTW(ElementwiseProblem):
    
    def __init__(self):
        super().__init__(n_var = N, 
                         n_obj = 2, 
                         n_eq_constr = 1, 
                         vtype = int)
    
    def evaluate_fitness(self, x):
        distance = 0
        c_dem = 0
        c_dist = 0
        early_time = 0
        late_time = 0
        # penalty = 0
        
        for i in range(1, len(matrix)):
            if c_dem <= 3:
                distance += matrix[x[i-1]][x[i]]
                c_dist += matrix[x[i-1]][x[i]]
                if (time_windows[x[i]][1] - c_dist) >= 0:
                    pass
                else:
                    early_time += abs(time_windows[x[i]][0] - c_dist)
                    late_time += abs(time_windows[x[i]][1] - c_dist)
                    # penalty += 1000
                c_dem += 1
            else:
                distance += matrix[x[i-1]][x[0]]
                c_dem = 1
                distance += matrix[x[0]][x[i]]
                c_dist = matrix[x[0]][x[i]]
                if (time_windows[x[i]][1] - c_dist) >= 0:
                    pass
                else:
                    early_time += abs(time_windows[x[i]][0] - c_dist)
                    late_time += abs(time_windows[x[i]][1] - c_dist)
                    # penalty += 1000
        distance += matrix[x[-1]][x[0]]
                
        return (distance, late_time) # penalty
        
    def _evaluate(self, x, out, *args, **kwargs):
        f1 = self.evaluate_fitness(x)[0]
        f2 = self.evaluate_fitness(x)[1]
        # f3 = self.evaluate_fitness(x)[2]
        
        h = x[0]
        
        out["F"] = [f1, f2]
        out["H"] = h
        
vrptw_problem = VRPTW()

vrptw_algorithm = NSGA2(pop_size = 100, 
                        sampling = PermutationRandomSampling(), 
                        crossover = OrderCrossover(prob = 0.8, repair = RoundingRepair()), 
                        mutation = InversionMutation(prob = 0.1), 
                        eliminate_duplicates = True)
 
termination_criteria = get_termination("n_gen", 100)

res = minimize(problem = vrptw_problem, 
               algorithm = vrptw_algorithm, 
               termination = termination_criteria, 
               seed = 7, 
               save_history = True, 
               verbose = True)

X_res = res.X
F_res = res.F

if len(X_res[0]) > 1:
    for res in sorted(list(zip(F_res, X_res)), key = lambda x : x[0][1]):
        print(res[0], res[1])
else:
    print(zip(F_res, X_res))

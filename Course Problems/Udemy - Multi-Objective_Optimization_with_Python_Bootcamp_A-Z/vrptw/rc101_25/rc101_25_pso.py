from rc101_25_data import matrix, demands, time_array, service_time, capacity, max_time

from pymoo.core.problem import ElementwiseProblem
from pymoo.algorithms.soo.nonconvex.pso import PSO
from pymoo.operators.sampling.rnd import PermutationRandomSampling
from pymoo.operators.repair.rounding import RoundingRepair
from pymoo.operators.crossover.ox import OrderCrossover
from pymoo.operators.mutation.inversion import InversionMutation
from pymoo.termination import get_termination
from pymoo.optimize import minimize

N = len(matrix)

class VRPTW(ElementwiseProblem):
    
    def __init__(self):
        super().__init__(n_obj = 1, 
                         n_eq_constr = 1, 
                         n_var = N, 
                         xl = 1, 
                         xu = N-1, 
                         vtype = int)
    
    def fitness(self, x):
        distance = 0
        cumu_dem = 0
        cumu_time = 0
        # routes = 1
        
        for i in range(1, N):
            if cumu_time + matrix[x[i-1]][x[i]] <= time_array[x[i]][1] and cumu_dem <= capacity: #  and cumu_dem <= capacity
                distance += matrix[x[i-1]][x[i]]
                cumu_time += matrix[x[i-1]][x[i]]
                if cumu_time < time_array[x[i]][0]:
                    cumu_time = time_array[x[i]][0]
                if cumu_time > time_array[x[i]][1]:
                    # tardiness += cumu_time - time_array[x[i]][1]
                    cumu_time += service_time
                else:
                    cumu_time += service_time
                # cumu_dem += demands[x[i]]
            else:
                distance += matrix[x[i-1]][x[0]]
                cumu_time = time_array[x[i]][0]
                # routes += 1
                if cumu_time > time_array[x[i]][1]:
                    # tardiness += cumu_time - time_array[x[i]][1]
                    cumu_time += service_time
                else:
                    cumu_time += service_time
                distance += matrix[x[0]][x[i]]
                # cumu_dem = demands[x[i]]
        distance += matrix[x[-1]][x[0]]
        
        return distance
    
    def _evaluate(self, x, out, *args, **kwargs):
        f1 = self.fitness(x)
        # f2 = self.fitness(x)[1]
        # f3 = self.fitness(x)[2]
        
        h = x[0]
        
        out["F"] = f1
        out["H"] = h
        
vrptw_problem = VRPTW()

vrptw_algorithm = PSO(pop_size = 100, 
                      sampling = PermutationRandomSampling(), 
                      w = 0.9, 
                      c1 = 2.0, 
                      c2 = 2.0, 
                      repair = RoundingRepair())

termination_criteria = get_termination("n_gen", 240)

res = minimize(problem = vrptw_problem, 
               algorithm = vrptw_algorithm, 
               termination = termination_criteria, 
               seed = 7, 
               save_history = True, 
               verbose = True)

print(res.F)
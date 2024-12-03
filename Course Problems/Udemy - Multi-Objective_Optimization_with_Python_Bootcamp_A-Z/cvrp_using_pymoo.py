import numpy as np
from pymoo.core.problem import ElementwiseProblem
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.operators.sampling.rnd import PermutationRandomSampling
from pymoo.operators.repair.rounding import RoundingRepair
from pymoo.operators.crossover.ox import OrderCrossover
from pymoo.operators.mutation.inversion import InversionMutation
from pymoo.termination import get_termination
from pymoo.optimize import minimize

matrix = np.array([
      [0, 548, 776, 696, 582, 274, 502, 194, 308, 194, 536, 502, 388, 354, 468, 776, 662],
      [548, 0, 684, 308, 194, 502, 730, 354, 696, 742, 1084, 594, 480, 674, 1016, 868, 1210],
      [776, 684, 0, 992, 878, 502, 274, 810, 468, 742, 400, 1278, 1164, 1130, 788, 1552, 754],
      [696, 308, 992, 0, 114, 650, 878, 502, 844, 890, 1232, 514, 628, 822, 1164, 560, 1358],
      [582, 194, 878, 114, 0, 536, 764, 388, 730, 776, 1118, 400, 514, 708, 1050, 674, 1244],
      [274, 502, 502, 650, 536, 0, 228, 308, 194, 240, 582, 776, 662, 628, 514, 1050, 708],
      [502, 730, 274, 878, 764, 228, 0, 536, 194, 468, 354, 1004, 890, 856, 514, 1278, 480],
      [194, 354, 810, 502, 388, 308, 536, 0, 342, 388, 730, 468, 354, 320, 662, 742, 856],
      [308, 696, 468, 844, 730, 194, 194, 342, 0, 274, 388, 810, 696, 662, 320, 1084, 514],
      [194, 742, 742, 890, 776, 240, 468, 388, 274, 0, 342, 536, 422, 388, 274, 810, 468],
      [536, 1084, 400, 1232, 1118, 582, 354, 730, 388, 342, 0, 878, 764, 730, 388, 1152, 354],
      [502, 594, 1278, 514, 400, 776, 1004, 468, 810, 536, 878, 0, 114, 308, 650, 274, 844],
      [388, 480, 1164, 628, 514, 662, 890, 354, 696, 422, 764, 114, 0, 194, 536, 388, 730],
      [354, 674, 1130, 822, 708, 628, 856, 320, 662, 388, 730, 308, 194, 0, 342, 422, 536],
      [468, 1016, 788, 1164, 1050, 514, 514, 662, 320, 274, 388, 650, 536, 342, 0, 764, 194],
      [776, 868, 1552, 560, 674, 1050, 1278, 742, 1084, 810, 1152, 274, 388, 422, 764, 0, 798],
      [662, 1210, 754, 1358, 1244, 708, 480, 856, 514, 468, 354, 844, 730, 536, 194, 798, 0],
    ])

demands_list = np.array([0, 1, 1, 2, 4, 2, 4, 8, 8, 1, 2, 1, 2, 4, 4, 8, 8])
vehicle_capacities = np.array([15, 15, 15, 15])

N = len(matrix)

class CVRP(ElementwiseProblem):
    
    def __init__(self):
        self.matrix = matrix
        self.demands_list = demands_list
        self.vehicle_capacities = vehicle_capacities
        super().__init__(n_var = N, 
                         n_obj = 1, 
                         n_eq_constr = 1, 
                         vtype = int)
                        # Redundant
                        # xl = 1, 
                        # xu = N,
        
    def fitness_function(self, x):        
        distance = 0
        c_dem = 0

        for i in range(1, len(self.matrix)):
            if c_dem + self.demands_list[x[i]] <= self.vehicle_capacities[0]:
                distance += self.matrix[x[i-1]][x[i]]
                c_dem += self.demands_list[x[i]]
            else:
                distance += self.matrix[x[i-1]][x[0]]
                c_dem = self.demands_list[x[i]]
                distance += self.matrix[0][x[i]]
        distance += self.matrix[x[-1]][0]
        
        return distance

    def _evaluate(self, x, out, *args, **kwargs):
        f = self.fitness_function(x)
        
        out["F"] = f
        out["H"] = x[0]

cvrp_problem = CVRP()

cvrp_algorithm = NSGA2(
    pop_size = 100, 
    sampling = PermutationRandomSampling(), 
    crossover = OrderCrossover(prob = 0.9, repair = RoundingRepair()), 
    mutation = InversionMutation(prob = 0.1), 
    eliminate_duplicates = True
    )

termination_criteria = get_termination("n_gen", 50)

res = minimize(problem = cvrp_problem, 
               algorithm = cvrp_algorithm, 
               termination = termination_criteria, 
               seed = 7, 
               save_history = True, 
               verbose = True)

X_res = res.X
F_res = res.F

# for result in X_res:
#     print(result)

print(X_res[0])    
print(F_res[0][0])
        

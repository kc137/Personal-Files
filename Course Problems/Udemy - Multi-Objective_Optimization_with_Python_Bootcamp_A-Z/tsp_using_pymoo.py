import numpy as np, random
from pymoo.core.problem import ElementwiseProblem
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.operators.sampling.rnd import PermutationRandomSampling
from pymoo.operators.repair.rounding import RoundingRepair
from pymoo.operators.crossover.ox import OrderCrossover
from pymoo.operators.mutation.inversion import InversionMutation
from pymoo.operators.mutation.gauss import GM
from pymoo.termination import get_termination
from pymoo.optimize import minimize

N = 15
matrix = [ [0, 2448, 791, 1420, 2136, 94, 1634, 2451, 1373, 2573, 1783, 890, 1371, 532, 634], [2448, 0, 1745, 1375, 371, 2340, 1185, 164, 1436, 344, 1320, 2448, 1383, 1906, 2274], [791, 1745, 0, 937, 1743, 787, 1019, 1682, 959, 1842, 1090, 1028, 802, 357, 557], [1420, 1375, 937, 0, 1130, 1506, 197, 1184, 239, 1613, 165, 1156, 358, 1189, 1338], [2136, 371, 1743, 1130, 0, 2034, 893, 355, 1160, 358, 1399, 2136, 1486, 1705, 2057], [94, 2340, 787, 1506, 2034, 0, 1561, 2361, 1320, 2530, 1717, 983, 1437, 629, 604], [1634, 1185, 1019, 197, 893, 1561, 0, 1177, 433, 1573, 360, 1437, 151, 1029, 1449], [2451, 164, 1682, 1184, 355, 2361, 1177, 0, 1606, 250, 1312, 2451, 1458, 1910, 2283], [1373, 1436, 959, 239, 1160, 1320, 433, 1606, 0, 1464, 330, 1166, 479, 1052, 1270], [2573, 344, 1842, 1613, 358, 2530, 1573, 250, 1464, 0, 1474, 2573, 1690, 1956, 2347], [1783, 1320, 1090, 165, 1399, 1717, 360, 1312, 330, 1474, 0, 1783, 1138, 1236, 1513], [890, 2448, 1028, 1156, 2136, 983, 1437, 2451, 1166, 2573, 1138, 0, 1305, 867, 897], [1371, 1383, 802, 358, 1486, 1437, 151, 1458, 479, 1690, 1236, 1305, 0, 880, 1084], [532, 1906, 357, 1189, 1705, 629, 1029, 1910, 1052, 1956, 1513, 867, 880, 0, 638], [634, 2274, 557, 1338, 2057, 604, 1449, 2283, 1270, 2347, 1513, 897, 1084, 638, 0] ]

class TSP(ElementwiseProblem):
    
    def __init__(self):
        super().__init__(n_var = N, 
                         n_obj = 1, 
                         xl = 0, 
                         xu = N, 
                         vtype = int)
        
    
    def fitness_function(self, x):
        distance = 0
        for i in range(len(x) - 1):
            distance += matrix[x[i]][x[i+1]]
        distance += matrix[x[0]][x[-1]]
        return distance
        
    
    def _evaluate(self, x, out, *args, **kwargs):
        f = self.fitness_function(x)
        
        out["F"] = [f]


tsp_problem = TSP()

tsp_algorithm = NSGA2(
    pop_size = 100, 
    sampling = PermutationRandomSampling(), 
    crossover = OrderCrossover(prob = 0.9, repair = RoundingRepair()), 
    mutation = InversionMutation(prob = 0.1), 
    eliminate_duplicates = True
    )

termination_criteria = get_termination("n_gen", 50)

res = minimize(problem = tsp_problem, 
               algorithm = tsp_algorithm, 
               termination = termination_criteria, 
               seed = 7, 
               save_history = True, 
               verbose = True)

# print(tsp_problem.fitness_function(X))

X_res = res.X
F_res = res.F

print(X_res)
print(F_res[0])



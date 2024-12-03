from pymoo.core.problem import ElementwiseProblem
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.operators.sampling.rnd import PermutationRandomSampling
from pymoo.operators.crossover.ox import OrderCrossover
from pymoo.operators.mutation.inversion import InversionMutation
from pymoo.operators.repair.rounding import RoundingRepair
from pymoo.termination import get_termination
from pymoo.optimize import minimize

from pymoo.config import Config
Config.warnings['not_compiled'] = False

from cvrp_33_dataset1 import demands, capacity, matrix

N = len(matrix)

class CVRP(ElementwiseProblem):
    
    def __init__(self):
        super().__init__(n_var = N, 
                         n_eq_constr = 1, 
                         n_obj = 1, 
                         vtype = int)
        
    def evaluate_fitness(self, x):
        distance = 0
        cumu_dem = 0
        
        for i in range(1, len(matrix)):
            if cumu_dem + demands[x[i]] <= capacity:
                cumu_dem += demands[x[i]]
                distance += matrix[x[i-1]][x[i]]
            else:
                distance += matrix[x[i-1]][0]
                cumu_dem = demands[x[i]]
                distance += matrix[0][x[i]]
        distance += matrix[x[-1]][0]
        
        return distance
    
    def _evaluate(self, x, out, *args, **kwargs):
        f = self.evaluate_fitness(x)
        h = x[0]
        
        out["F"] = f
        out["H"] = h
        
    
cvrp_problem = CVRP()

nsga_algorithm = NSGA2(pop_size = 400, 
                       sampling = PermutationRandomSampling(), 
                       crossover = OrderCrossover(prob = 0.8, repair = RoundingRepair()), 
                       mutation = InversionMutation(prob = 0.1), 
                       eliminate_duplicates = True)

termination_criteria = get_termination("n_gen", 50)

res = minimize(problem = cvrp_problem, 
               algorithm = nsga_algorithm, 
               termination = termination_criteria, 
               seed = 7, 
               save_history = True, 
               verbose = True)

X_res = res.X
F_res = res.F

# sols = X_res[0:min(5, len(X_res))]
if len(F_res) > 5:
    sols = X_res[0:min(5, len(F_res))]
    print(sols)
else:
    sols = X_res

with open("results.txt", "w") as solution:
    if len(sols) > 1:
        for sol in sols[0:min(5, len(sols))]:
            solution.write(f"Solution : {sols}\n")
    else:
        solution.write(f"Solution : {sols}\n")
print(F_res[0:min(5, len(F_res))])


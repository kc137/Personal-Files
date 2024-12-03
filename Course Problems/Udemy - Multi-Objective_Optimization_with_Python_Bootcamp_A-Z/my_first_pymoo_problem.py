import numpy as np
from pymoo.core.problem import ElementwiseProblem
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.operators.sampling.rnd import FloatRandomSampling
from pymoo.operators.crossover.sbx import SBX
from pymoo.operators.mutation.pm import PM
from pymoo.termination import get_termination
from pymoo.optimize import minimize

class FirstPymooProblem(ElementwiseProblem):
    
    def __init__(self):
        super().__init__(n_var = 3, 
                         n_obj = 2, 
                         n_ieq_constr = 2, 
                         xl = np.array([-10 for _ in range(3)]), 
                         xu = np.array([10 for _ in range(3)]))
        
    def _evaluate(self, x, out, *args, **kwargs):
        f1 = (x[0]**2 + x[1]**2 + x[2]**2)
        f2 = (-(x[0] - 1)**2 - (x[1] - 1)**2 - (x[2] - 1)**2)*(-1)
        
        g1 = x[0] + x[1] - x[2] - 1
        g2 = -3*x[0] + x[1] + x[2] + 4
        
        out["F"] = [f1, f2]
        out["G"] = [g1, g2]
        
        

problem_1 = FirstPymooProblem()

algorithm_1 = NSGA2(
    pop_size = 50, 
    sampling = FloatRandomSampling(), 
    crossover = SBX(prob = 0.9, eta = 20), 
    mutation = PM(eta = 25), 
    eliminate_duplicates = True
    )

termination_criteria = get_termination("n_gen", 100)

res = minimize(problem = problem_1, 
               algorithm = algorithm_1, 
               termination = termination_criteria, 
               seed = 7, 
               save_history = True, 
               verbose = True)
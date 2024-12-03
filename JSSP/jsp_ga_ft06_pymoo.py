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

from jsp_ga_ft06_data import machining_sequence, processing_times

NJ = len(processing_times)
NM = len(processing_times[0])

class CVRP(ElementwiseProblem):
    
    def __init__(self):
        super().__init__(n_var = NJ*NM, 
                         n_eq_constr = 0, 
                         n_obj = 1, 
                         vtype = int)
        
    def evaluate_fitness(self, x):
        keys = {k : 0 for k in range(1, NJ + 1)}
        j_time = {j : 0 for j in keys}
        m_time = {m : 0 for m in range(1, NM+1)}
        for n in x:
            j = n % NJ if n % NJ else NJ
            curr_m = machining_sequence[j-1][keys[j]]
            processing_time = processing_times[j-1][keys[j]]
            j_time[j] += processing_time
            m_time[curr_m] += processing_time
            
            j_time[j] = max(j_time[j], m_time[curr_m])
            m_time[curr_m] = max(m_time[curr_m], j_time[j])
            
            keys[j] += 1
            
        makespan = max(j_time.values())
        return makespan
    
    def _evaluate(self, x, out, *args, **kwargs):
        f = self.evaluate_fitness(x)
        # h = x[0]
        
        out["F"] = f
        # out["H"] = h
        
    
cvrp_problem = CVRP()

nsga_algorithm = NSGA2(pop_size = 60, 
                       sampling = PermutationRandomSampling(), 
                       crossover = OrderCrossover(prob = 0.8, repair = RoundingRepair()), 
                       mutation = InversionMutation(prob = 0.1), 
                       eliminate_duplicates = True)

termination_criteria = get_termination("n_gen", 100)

res = minimize(problem = cvrp_problem, 
               algorithm = nsga_algorithm, 
               termination = termination_criteria, 
               seed = 7, 
               save_history = True, 
               verbose = True)

X_res = res.X
F_res = res.F

sols = X_res[0:min(5, len(X_res))]
if len(F_res) > 5:
    sols = X_res[0:min(5, len(F_res))]
    print(sols)
else:
    sols = X_res

# with open("results.txt", "w") as solution:
#     if len(sols) > 1:
#         for sol in sols[0:min(5, len(sols))]:
#             solution.write(f"Solution : {sols}\n")
#     else:
#         solution.write(f"Solution : {sols}\n")
print(F_res[:5])


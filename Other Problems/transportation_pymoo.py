import numpy as np, random
from pymoo.core.problem import ElementwiseProblem
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.operators.sampling.rnd import BinaryRandomSampling
from pymoo.operators.crossover.pntx import TwoPointCrossover
from pymoo.operators.mutation.bitflip import BitflipMutation
from pymoo.termination import get_termination
from pymoo.optimize import minimize

R, C = 3, 4
supply = [50, 50, 50]
demand = [45, 15, 40, 50]
var_matrix = [[1 for _ in range(C)] for _ in range(R)]
var_matrix = [[0, 1, 0, 1], [0, 0, 1, 1], [1, 0, 1, 0]]
cost_matrix = [[8, 10, 6, 3], [9, 15, 8, 6], [5, 12, 5, 7]]

N = R*C

class Transportation(ElementwiseProblem):
    
    def __init__(self):
        super().__init__(n_var = N, 
                         n_obj = 1, 
                         x1 = 0, 
                         xu = 1, 
                         vtype = int)
        self.min_cost = 10e5
        self.best_elements = []
    
    def fitness_function(self, x, elements):
        demand_temp = demand[:]
        supply_temp = supply[:]
        cost = 0
        r, c = 0, 0
        
        for i in elements:
            c = i % C
            r = i // C
            if x[i]:
                if supply_temp[r] == 0 or demand_temp[c] == 0:
                    cost += 1000
                else:
                    to_use = min(supply_temp[r], demand_temp[c])
                    cost += x[i]*cost_matrix[r][c]*to_use
                    demand_temp[c] -= to_use
                    supply_temp[r] -= to_use
            # if (i+1) % C == 0:
            #     r += 1
                    
        for dem in demand_temp:
            if dem:
                cost += 1000
        
        for sup in supply_temp:
            if sup:
                cost += 1000
        
        return cost
    
    def _evaluate(self, x, out, *args, **kwargs):
        elements = list(range(R*C))
        random.shuffle(elements)
        f = self.fitness_function(x, elements)
        
        if f < self.min_cost:
            self.best_elements = elements
        
        out["F"] = [f]

transportation_problem = Transportation()

transportation_algo = NSGA2(
    pop_size = 100, 
    sampling = BinaryRandomSampling(), 
    crossover = TwoPointCrossover(prob = 0.85), 
    mutation = BitflipMutation(prob = 0.1), 
    eliminate_duplicates = True
    )

termination_criteria = get_termination("n_gen", 100)

res = minimize(
    problem = transportation_problem, 
    algorithm = transportation_algo, 
    termination = termination_criteria, 
    seed = 7, # random.randint(1, 100), 
    save_history = True, 
    verbose = True
    )

X_res = res.X
F_res = res.F

print(X_res)
print(F_res)
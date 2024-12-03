import random

R, C = 3, 4
supply = [300, 400, 500]
demand = [250, 350, 400, 200]
# var_matrix = [[1 for _ in range(C)] for _ in range(R)]
# var_matrix = [[1, 1, 0, 0], [0, 1, 1, 0], [0, 0, 1, 1]]
# var_matrix = [[0, 1, 0, 0], [1, 0, 1, 0], [0, 1, 1, 1]]
var_matrix = [[0, 1, 1, 1], [1, 0, 0, 0], [1, 0, 0, 0]]

cost_matrix = [[3, 1, 7, 4], [2, 6, 5, 9], [8, 3, 3, 2]]

res_table = [[0]*C for _ in range(R)]

R, C = 3, 4
supply = [50, 50, 50]
demand = [45, 15, 40, 50]
var_matrix = [[1 for _ in range(C)] for _ in range(R)]
var_matrix = [[0, 1, 0, 1], [0, 0, 1, 1], [1, 0, 1, 0]]
var_matrix = [[0, 1, 0, 1], [0, 0, 1, 1], [1, 0, 1, 0]]
cost_matrix = [[8, 10, 6, 3], [9, 15, 8, 6], [5, 12, 5, 7]]

def get_cost():
    demand_temp = demand[:]
    supply_temp = supply[:]
    cost = 0
    for r in range(R):
        for c in range(C):
            if var_matrix[r][c]:
                if supply_temp[r] == 0 or demand_temp[c] == 0:
                    cost += 1000
                else:
                    to_use = min(supply_temp[r], demand_temp[c])
                    cost += var_matrix[r][c]*cost_matrix[r][c]*to_use
                    demand_temp[c] -= to_use
                    supply_temp[r] -= to_use
                    
    print(demand_temp, supply_temp)
    for dem in demand_temp:
        if dem:
            cost += 1000
    for sup in supply_temp:
        if sup:
            cost += 1000
            
    print(cost)
    return cost

get_cost()



"""
Initial Function that I created
def get_cost():
    cost = 0
    for r in range(R):
        for c in range(C):
            cost += var_matrix[r][c]*cost_matrix[r][c]
    for r in range(R):
        curr_dem = 0
        for c in range(C):
            curr_dem += var_matrix[r][c]*demand[c]
        if curr_dem != supply[r]:
            cost += 1000
    return cost
"""

"""
Pymoo
"""

R, C = 3, 4
supply = [50, 50, 50]
demand = [45, 15, 40, 50]
var_matrix = [[1 for _ in range(C)] for _ in range(R)]
var_matrix = [[0, 1, 0, 1], [0, 0, 1, 1], [1, 0, 1, 0]]
var_matrix = [0, 1, 1, 1 ,1, 0, 0, 0, 1, 0, 0, 0]
cost_matrix = [[8, 10, 6, 3], [9, 15, 8, 6], [5, 12, 5, 7]]

N = R*C

def fitness_function(x):
    demand_temp = demand[:]
    supply_temp = supply[:]
    cost = 0
    r, c = 0, 0
    
    elements = list(range(R*C))
    random.shuffle(elements)
    print(elements)
    
    for i in elements:
        c = i % C
        r = i // C
        print(r, c)
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
    
    print(demand_temp, supply_temp)
    for dem in demand_temp:
        if dem:
            cost += 1000
    
    for sup in supply_temp:
        if sup:
            cost += 1000
    
    return cost

print(fitness_function(var_matrix))
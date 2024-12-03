import numpy as np, math


N = 32

coords = []
demands = []
matrix = np.zeros(shape = [N, N], dtype = int)

with open("A-n32-k5.vrp", "r") as data:
    lines = data.read().splitlines()
    capacity = int(lines[5].split()[-1])
    
    for line in lines[7:39]:
        coord_str = line.split()
        x, y = int(coord_str[1]), int(coord_str[2])
        coords.append((x, y))
    
    for line in lines[40:72]:
        demand_str = line.split()
        demand = int(demand_str[1])
        demands.append(demand)

for p1 in range(N):
    for p2 in range(N):
        if p1 != p2:
            matrix[p1][p2] = math.hypot(coords[p1][0] - coords[p2][0], 
                                         coords[p1][1] - coords[p2][1])
import math, numpy as np

coords = []
demands = []

with open("DataSet-1.txt", "r") as data:
    lines = data.read().strip().splitlines()
    
    for line in lines[7:40]:
        coord = line.strip().split()
        coords.append((int(coord[1]), int(coord[2])))
    
    for line in lines[41:74]:
        demand = line.strip().split()
        demands.append(int(demand[1]))
    
    capacity = int(lines[5].split()[-1])

matrix_list = [[0 for _ in range(len(coords))] for _ in range(len(coords))]
matrix = np.array(matrix_list)

demands = np.array(demands)

for p1 in range(len(coords)):
    for p2 in range(len(coords)):
        if p1 != p2:
            matrix[p1][p2] = round(math.hypot(coords[p1][0] - coords[p2][0], 
                                               coords[p1][1] - coords[p2][1]))
        
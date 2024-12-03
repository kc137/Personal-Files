import numpy as np, math

coords = []
time_array = []
demands = []
service_time = 10

N = 101

matrix = np.zeros(shape = [N, N], dtype = float)

with open("RC101.txt", "r") as data:
    lines = data.read().splitlines()
    capacity = int(lines[4].split()[-1])
    
    for line in lines[9:]:
        line = line.split()
        coords.append((int(line[1]), int(line[2])))
        demands.append(int(line[3]))
        time_array.append((int(line[4]), int(line[5])))
        
for p1 in range(len(coords)):
    for p2 in range(len(coords)):
        if p1 != p2:
            matrix[p1][p2] = round(math.hypot(coords[p1][0] - coords[p2][0], 
                                        coords[p1][1] - coords[p2][1]))

# coords = np.array(coords)
# time_array = np.array(time_array)
# demands = np.array(demands)
# matrix = np.array(matrix)

max_time = max(time_array[1:], key = lambda x : x[1])[-1]
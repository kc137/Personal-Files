import math, numpy as np

coords = []
demands = []
time_windows = []
service_time = []
NV = 4

with open("pr01.txt", "r") as data:
    lines = data.read().splitlines()
    fst_line = lines[0].split()
    ND, NC = int(fst_line[-1]), int(fst_line[-2])
    snd_line = lines[1].split()
    max_dur, Q = int(snd_line[0]), int(snd_line[1])
    
    for line in lines[5:]:
        sub_data = line.split()
        sub_data = [float(dat) for dat in sub_data]
        coords.append((sub_data[1], sub_data[2]))
        service_time.append(sub_data[3])
        demands.append(sub_data[4])
        time_windows.append((sub_data[-2], sub_data[-1]))

N = len(coords)
distance_matrix = np.zeros(shape = (N, N), dtype = float)

for i in range(N):
    for j in range(N):
        if i != j:
            distance_matrix[i][j] = math.hypot(coords[i][0] - coords[j][0], 
                                               coords[i][1] - coords[j][1])
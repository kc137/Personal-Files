import numpy as np


x = [0, 12, 13, 15, 11, 7, 4, 3, 1, 5, 6, 2, 10, 9, 8, 14, 16]
matrix = np.array([
        [0, 6, 9, 8, 7, 3, 6, 2, 3, 2, 6, 6, 4, 4, 5, 9, 7],
        [6, 0, 8, 3, 2, 6, 8, 4, 8, 8, 13, 7, 5, 8, 12, 10, 14],
        [9, 8, 0, 11, 10, 6, 3, 9, 5, 8, 4, 15, 14, 13, 9, 18, 9],
        [8, 3, 11, 0, 1, 7, 10, 6, 10, 10, 14, 6, 7, 9, 14, 6, 16],
        [7, 2, 10, 1, 0, 6, 9, 4, 8, 9, 13, 4, 6, 8, 12, 8, 14],
        [3, 6, 6, 7, 6, 0, 2, 3, 2, 2, 7, 9, 7, 7, 6, 12, 8],
        [6, 8, 3, 10, 9, 2, 0, 6, 2, 5, 4, 12, 10, 10, 6, 15, 5],
        [2, 4, 9, 6, 4, 3, 6, 0, 4, 4, 8, 5, 4, 3, 7, 8, 10],
        [3, 8, 5, 10, 8, 2, 2, 4, 0, 3, 4, 9, 8, 7, 3, 13, 6],
        [2, 8, 8, 10, 9, 2, 5, 4, 3, 0, 4, 6, 5, 4, 3, 9, 5],
        [6, 13, 4, 14, 13, 7, 4, 8, 4, 4, 0, 10, 9, 8, 4, 13, 4],
        [6, 7, 15, 6, 4, 9, 12, 5, 9, 6, 10, 0, 1, 3, 7, 3, 10],
        [4, 5, 14, 7, 6, 7, 10, 4, 8, 5, 9, 1, 0, 2, 6, 4, 8],
        [4, 8, 13, 9, 8, 7, 10, 3, 7, 4, 8, 3, 2, 0, 4, 5, 6],
        [5, 12, 9, 14, 12, 6, 6, 7, 3, 3, 4, 7, 6, 4, 0, 9, 2],
        [9, 10, 18, 6, 8, 12, 15, 8, 13, 9, 13, 3, 4, 5, 9, 0, 9],
        [7, 14, 9, 16, 14, 8, 5, 10, 6, 5, 4, 10, 8, 6, 2, 9, 0],
    ])

time_windows = np.array([
        (0, 5),  # depot
        (7, 12),  # 1
        (10, 15),  # 2
        (16, 18),  # 3
        (10, 13),  # 4
        (0, 5),  # 5
        (5, 10),  # 6
        (0, 4),  # 7
        (5, 10),  # 8
        (0, 3),  # 9
        (10, 16),  # 10
        (10, 15),  # 11
        (0, 5),  # 12
        (5, 10),  # 13
        (7, 8),  # 14
        (10, 15),  # 15
        (11, 15),  # 16
    ])

def evaluate_fitness(x):
    distance = 0
    c_dem = 0
    c_dist = 0
    early_time = 0
    late_time = 0
    
    for i in range(1, len(matrix)):
        if c_dem <= 3:
            print(f"Distance-{x[i-1]}-{x[i]} : {matrix[x[i-1]][x[i]]}")
            distance += matrix[x[i-1]][x[i]]
            c_dist += matrix[x[i-1]][x[i]]
            early_time += (time_windows[x[i]][0] - c_dist)
            late_time += (time_windows[x[i]][1] - c_dist)
            c_dem += 1
        else:
            print(f"Distance-{x[i-1]}-{x[0]} : {matrix[x[i-1]][x[0]]}")
            distance += matrix[x[i-1]][x[0]]
            c_dem = 1
            print(f"Distance-{0}-{x[i]} : {matrix[x[0]][x[i]]}")
            distance += matrix[x[0]][x[i]]
            c_dist = matrix[x[0]][x[i]]
            early_time = (time_windows[x[i]][0] - c_dist)
            late_time = (time_windows[x[i]][1] - c_dist)
    print(f"Distance-{x[-1]}-{0} : {matrix[x[-1]][x[0]]}")
    distance += matrix[x[-1]][x[0]]
            # early_time += abs(time_windows[x[-1]][0] - c_dist)
            # late_time += abs(time_windows[x[-1]][1] - c_dist)
            
    return (distance, late_time)

print(evaluate_fitness(x))

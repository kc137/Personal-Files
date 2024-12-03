import math, numpy as np

NV = 5
coords = []
demands = []

with open("Instances/A-n33-k5.vrp", "r") as data:
    lines = data.read().splitlines()
    capacity = int(lines[5].split()[-1])
    for line in lines[7:40]:
        line_str = line.split()
        coords_str = [int(line_str[0]), int(line_str[1])]
        coords.append(tuple(coords_str))
    for line in lines[41:74]:
        line_str = line.split()
        demands.append(int(line_str[1]))

matrix = [[] for _ in range(len(coords))]

for p1 in range(len(coords)):
    for p2 in range(len(coords)):
        if p1 != p2:
            matrix[p1].append(
                round(math.hypot(coords[p1][0] - coords[p2][0], coords[p1][1] - coords[p2][1]))
                )
            # matrix[p1].append(
            #     (math.hypot(coords[p1][0] - coords[p2][0], coords[p1][1] - coords[p2][1]))
            #     )
        else:
            matrix[p1].append(0)
            
# matrix = np.zeros(shape = [len(coords), len(coords)], dtype = float)

# for p1 in range(len(coords)):
#     for p2 in range(len(coords)):
#         if p1 != p2:
#             matrix[p1][p2] = np.round(math.hypot(coords[p1][0] - coords[p2][0], 
#                                         coords[p1][1] - coords[p2][1]))

routes = {1: [4, 2, 10, 30, 32, 7],
 2: [13, 11, 12, 16, 29, 24, 23],
 3: [14, 9, 8, 3, 5, 6],
 4: [15, 17, 18, 22, 19, 20],
 5: [31, 28, 26, 25, 21, 27, 33]}

# dem_check = {r : 0 for r in routes}

"""
Route #1: 15 17 9 3 16 29
Route #2: 12 5 26 7 8 13 32 2
Route #3: 20 4 27 25 30 10
Route #4: 23 28 18 22
Route #5: 24 6 19 14 21 1 31 11
cost 661

"""

sol_routes = [
    [0, 15, 17, 9, 3, 16, 29, 0], 
    [0, 12, 5, 26, 7, 8, 13, 32, 2, 0], 
    [0, 20, 4, 27, 25, 30, 10, 0], 
    [0, 23, 28, 18, 22, 0], 
    [0, 24, 6, 19, 14, 21, 1, 31, 11, 0]
    ]

distance = 0

for r in sol_routes:
    for i in range(len(r) - 1):
        distance += matrix[r[i]][r[i+1]]

# for r in routes:
#     for c in routes[r]:
#         dem_check[r] += demands[c-1]
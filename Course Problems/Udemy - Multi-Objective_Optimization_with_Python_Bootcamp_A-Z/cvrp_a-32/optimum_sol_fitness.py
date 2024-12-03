import random
from numpy.random import randint
from cvrp_a_32_sa_data import matrix

tours = [7, 4, 5, 22, 3, 31, 12, 6, 25, 30, 20, 16, 11, 19, 8, 13, 18, 9, 24, 21, 29, 15, 17, 14, 28, 23, 10, 1, 27, 26, 2]

N = len(tours)

best = "0 21 31 19 17 13 7 26 0 12 1 16 30 0 27 24 0 29 18 8 9 22 15 10 25 5 20 0 14 28 11 4 23 3 2 6 0"
best = best.split()

best = [int(num) for num in best]

distance = 0
for i in range(len(best) - 1):
    print(f"Route - {best[i]}-{best[i+1]}")
    distance += matrix[best[i]][best[i+1]]
print(distance)
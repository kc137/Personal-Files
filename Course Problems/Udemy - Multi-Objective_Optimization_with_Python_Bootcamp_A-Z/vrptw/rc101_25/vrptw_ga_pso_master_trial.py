# from rc101_25_data import matrix, time_array, service_time, demands, capacity
from rc101_100_data import matrix, time_array, service_time, demands, capacity

# x = [0, 87, 16, 30, 0, 
#      0, 51, 57, 99, 97, 21, 0, 
#      0, 94, 56, 36, 37, 88, 53, 0, 
#      0, 81, 64, 20, 85, 62, 0, 
#      0, 8, 5, 2, 100, 12, 60, 0, 
#      0, 15, 83, 82, 59, 9, 0, 
#      0, 77, 75, 78, 1, 0, 
#      0, 17, 47, 40, 38, 0, 
#      0, 18, 84, 32, 66, 0, 
#      0, 76, 33, 27, 0, 
#      0, 7, 45, 61, 41, 0, 
#      0, 89, 31, 67, 19, 0, 
#      0, 44, 42, 50, 54, 0, 
#      0, 63, 28, 22, 0, 
#      0, 14, 95, 6, 0, 
#      0, 25, 74, 24, 13, 10, 11, 0, 
#      0, 80, 98, 26, 72, 0, 
#      0, 86, 58, 23, 48, 49, 93, 96, 0, 
#      0, 79, 73, 35, 0, 
#      0, 52, 65, 68, 4, 92, 0, 
#      0, 39, 43, 46, 70, 55, 90, 91, 0, 
#      0, 69, 71, 29, 34, 0, 
#      0, 3, 0]

x = [0, 6, 2, 8, 5, 3, 7, 13, 0, 
     0, 22, 21, 23, 9, 25, 24, 0, 
     0, 12, 14, 15, 16, 17, 1, 4, 0, 
     0, 10, 11, 19, 18, 20, 0]

N = len(x)

def fitness(x):
    distance = 0
    cumu_dem = 0
    tardiness = 0
    cumu_time = 0
    routes = 1
    
    for i in range(N-1):
        distance += matrix[x[i]][x[i+1]]
        print(f"Route {x[i]} - {x[i+1]} - {distance}")
    
    return distance

print(fitness(x))
from rc101_100_data import matrix, demands, time_array, service_time, capacity, max_time

routes = []

with open("RC101.sol", "r") as data:
    lines = data.read().splitlines()
    for line in lines:
        route = line.strip().split(":")
        route = route[-1].split()
        if line != lines[-1]:
            route_int = [0] + [int(r) for r in route[:len(route)]] + [0]
            routes.append(route_int)
N = len(matrix)

x = [0]

def fitness(x):
    distance = 0
    cumu_dem = 0
    tardiness = 0
    cumu_time = 0
    routes = 1
    
    for i in range(1, N):
        if cumu_time + matrix[x[i-1]][x[i]] <= time_array[x[i]][1]: #  and cumu_dem <= capacity
            distance += matrix[x[i-1]][x[i]]
            cumu_time += matrix[x[i-1]][x[i]]
            if cumu_time < time_array[x[i]][0]:
                cumu_time = time_array[x[i]][0]
            if cumu_time > time_array[x[i]][1]:
                tardiness += cumu_time - time_array[x[i]][1]
                cumu_time += service_time
            else:
                cumu_time += service_time
            cumu_dem += demands[x[i]]
            print(f"Route-{routes} - {x[i-1]}-{x[i]} - Time - {(round(cumu_time - 10, 1), round(cumu_time, 1))} - {(time_array[x[i]][0], time_array[x[i]][1])} - Delay - {cumu_time > time_array[x[i]][1]}")
        else:
            distance += matrix[x[i-1]][x[0]]
            print(f"Route-{routes} - {x[i-1]}-{x[0]} - Time - {(round(cumu_time - 10, 1), round(cumu_time, 1))} - {(time_array[x[0]][0], time_array[x[0]][1])} - Delay - {cumu_time > time_array[x[0]][1]}")
            routes += 1
            cumu_time = time_array[x[i]][0]
            print(f"Route-{routes} - {x[0]}-{x[i]} - Time - {(round(cumu_time - 10, 1), round(cumu_time, 1))} - {(time_array[x[i]][0], time_array[x[i]][1])} - Delay - {cumu_time > time_array[x[i]][1]}")
            if cumu_time > time_array[x[i]][1]:
                tardiness += cumu_time - time_array[x[i]][1]
                cumu_time += service_time
            else:
                cumu_time += service_time
            distance += matrix[x[0]][x[i]]
            cumu_dem = demands[x[i]]
    distance += matrix[x[-1]][x[0]]
    print(f"Route-{routes} - {x[-1]}-{x[0]} - Time - {(round(cumu_time - 10, 1), round(cumu_time, 1))} - {(time_array[x[0]][0], time_array[x[0]][1])} - Delay - {cumu_time > time_array[x[0]][1]}")
    
    return (distance, routes)

distance = 0

routes_dict = {}
delays = 0

for route in routes:
    for node in route:
        if node != 0:
            x.append(node)

for route in routes:
    cumu_dist = 0
    for i in range(len(route) - 1):
        if i == len(route) - 2:
            cumu_dist += matrix[route[i]][route[i+1]]
        else:
            cumu_dist += matrix[route[i]][route[i+1]] + 10
        # print(routes[i], routes[i+1])
        routes_dict[(time_array[route[i+1]][0], time_array[route[i+1]][1])] = [cumu_dist, matrix[route[i]][route[i+1]]]
        delays += max(0, cumu_dist - time_array[route[i+1]][1])
        # if max(0, cumu_dist - time_array[route[i+1]][1]):
        #     print(f"Late : {route[i+1]}")
        distance += matrix[route[i]][route[i+1]]
print(distance)

print(fitness(x))
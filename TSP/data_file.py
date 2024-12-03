distance_matrix = []
time_windows = []

with open("rc_202.3.txt") as data:
    lines = data.read().splitlines()
    distances = []
    for line in lines[1:30]:
        curr = line.split()
        distances += curr
    
    print(len(distances))
    N = int(len(distances)**0.5)
    
    for i in range(N):
        single_row = []
        curr_row = i*N
        for j in range(N):
            single_row.append(float(distances[curr_row + j]))
        distance_matrix.append(single_row)
    
    for line in lines[30:]:
        line = line.split()
        time_windows.append((int(line[0]), int(line[1])))
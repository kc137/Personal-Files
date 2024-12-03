N = 7

DIST = [[0]*N for _ in range(N)]

with open("flight_tour_data.dat") as data:
    lines = data.read().splitlines()
    
    dist_lines = lines[2:8]
    upper_row = []
    for line in dist_lines:
        line = line.replace("DIST: ", "").replace("[", "").replace("]", "").replace("(", "").replace(")", "")
        line = line.split()
        dist_line = [int(n) for n in line[2:]]
        upper_row.append(dist_line)

for i in range(N):
    l = 0
    for j in range(N):
        if j > i:
            DIST[i][j] = upper_row[i][l]
            DIST[j][i] = upper_row[i][l]
            l += 1

DIST = []

with open("flight_tour_2_23_data.dat") as data:
    lines = data.read().splitlines()
    
    for line in lines[4:]:
        line = line.replace("[", "")\
                   .replace("]", "")\
                   .replace("(", "")\
                   .replace(")", "")\
                   .replace("DIST: ", "")
        curr_line = line.split()
        
        dist_line = [int(n) for n in curr_line[2:]]
        DIST.append(dist_line)

N = len(DIST)
DIST = []

with open("landings_data.dat") as data:
    lines = data.read().splitlines()
    
    start_line = lines[2]
    start_line = start_line.replace("[", "").replace("]", "").split()
    START = [int(n) for n in start_line[1:]]
    
    target_line = lines[3]
    target_line = target_line.replace("[", "").replace("]", "").split()
    TARGET = [int(n) for n in target_line[1:]]
    
    stop_line = lines[4]
    stop_line = stop_line.replace("[", "").replace("]", "").split()
    STOP = [int(n) for n in stop_line[1:]]
    
    early_line = lines[5]
    early_line = early_line.replace("[", "").replace("]", "").split()
    EARLY = [int(n) for n in early_line[1:]]
    
    late_line = lines[6]
    late_line = late_line.replace("[", "").replace("]", "").split()
    LATE = [int(n) for n in late_line[1:]]
    
    dist_lines = lines[9:19]
    for line in dist_lines:
        curr_line = line.replace("DIST: ", "").replace("[", "").replace("]", "")
        curr_line = curr_line.split()
        DIST.append([int(n) for n in curr_line])
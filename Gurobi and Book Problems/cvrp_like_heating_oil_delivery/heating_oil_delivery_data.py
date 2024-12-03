DIST = []
DEM = []
CAP = 39000

with open("heating_oil_delivery_data.dat") as data:
    lines = data.read().splitlines()
    
    dist_lines = lines[:7]
    for line in dist_lines:
        curr_line = line.replace("DIST: ", "").replace("[", "").replace("]", "")
        curr_line = curr_line.split()
        dist_line = [int(n) for n in curr_line]
        DIST.append(dist_line)
    
    dem_line = lines[8]
    curr_line = dem_line.replace("DEM: ", "").replace("[", "").replace("]", "").replace("(2)", "")
    curr_line = curr_line.split()
    DEM = [0] + [int(n) for n in curr_line]
    
    cap_line = lines[10]
    cap_line = cap_line.split()
    CAP = int(cap_line[1])
def run():
    COST = []
    with open("depots_data.dat") as data:
        lines = data.read().splitlines()
        
        cap_line = lines[4]
        cap_line = cap_line.replace("CAP: ", "").replace("[", "").replace("]", "")
        cap_line = cap_line.split()
        CAP = [int(c) for c in cap_line]
        
        cost_lines = lines[6:18]
        for line in cost_lines:
            line = line.replace("COST: ", "").replace("[", "").replace("]", "")
            cost_line = line.split()
            cost_line = [int(cost) for cost in cost_line]
            COST.append(cost_line)
            
        dem_line = lines[19]
        dem_line = dem_line.replace("DEM: ", "").replace("[", "").replace("]", "")
        dem_line = dem_line.split()
        DEM = [int(c) for c in dem_line]
        
        fix_line = lines[21]
        fix_line = fix_line.replace("CFIX: ", "").replace("[", "").replace("]", "")
        fix_line = fix_line.split()
        CFIX = [int(c) for c in fix_line]
    return CAP, COST, DEM, CFIX
        
data = run()
CAP = data[0]
COST = data[1]
DEM = data[2]
CFIX = data[3]
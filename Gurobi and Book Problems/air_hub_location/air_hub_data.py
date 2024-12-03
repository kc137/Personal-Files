
DIST = []
QUANT = []

with open("air_hub_data.dat") as data:
    lines = data.read().splitlines()
    
    dist_lines = lines[:6]
    for line in dist_lines:
        line = line.replace("DIST: ", "").replace("[", "").replace("]", "")
        line = line.split()
        dist_line = [int(n) for n in line]
        DIST.append(dist_line)
    
    quant_lines = lines[7:13]
    for line in quant_lines:
        line = line.replace("QUANT: ", "").replace("[", "").replace("]", "")
        line = line.split()
        quant_line = [int(n) for n in line]
        QUANT.append(quant_line)
    
FACTOR = 0.8
NAMES = ["Atlanta", "Boston", "Chicago", "Marseille", "Nice", "Paris"]
N_HUBS = 2
REQ = {}
CBUY = {}
CPROD = {}
CAP = {}
DEM = {}

def run():
    with open("c3toy.dat") as data:
        lines = data.read().splitlines()
        
        for line in lines[2:20]:
            line = line.replace("[", "").replace("]", "").replace("(", "").replace(")", "").replace("\"", "")
            curr = line.split()
            if curr[0] == "REQ:":
                REQ[(curr[1], curr[2])] = int(curr[3])
            else:
                REQ[(curr[0], curr[1])] = int(curr[2])
        
        for line in lines[21:36]:
            line = line.replace("[", "").replace("]", "").replace("(", "").replace(")", "").replace("\"", "")
            curr = line.split()
            if curr[0] =="CBUY:":
                CBUY[curr[1]] = float(curr[2])
            else:
                CBUY[curr[0]] = float(curr[1])
        
        for line in lines[37:42]:
            line = line.replace("[", "").replace("]", "").replace("(", "").replace(")", "").replace("\"", "")
            curr = line.split()
            if curr[0] =="ASSEMBLY:":
                CPROD[curr[1]] = float(curr[2])
                CAP[curr[1]] = int(curr[3])
            else:
                CPROD[curr[0]] = float(curr[1])
                CAP[curr[0]] = int(curr[2])
        
        for line in lines[43:45]:
            line = line.replace("[", "").replace("]", "").replace("(", "").replace(")", "").replace("\"", "")
            curr = line.split()
            if curr[0] == "DEM:":
                DEM[curr[1]] = int(curr[2])
            else:
                DEM[curr[0]] = int(curr[1])

run()

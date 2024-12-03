DEM = []

MASTER = []
indexes = [2, 4, 14, 16]

def run():
    with open("c4compo.dat") as data:
        lines = data.read().splitlines()
        
        for i in range(len(indexes)):
            line = lines[indexes[i]]
            curr = line.replace("[", "").replace("]", "")
            curr = curr.split()
            curr = [int(n) if n.isdigit() else float(n) for n in curr[1:]]
            MASTER.append(curr)
        
        for line in lines[9:13]:
            curr = line.replace("[", "").replace("]", "")
            curr = curr.split()
            if curr[0] == "DEM:":
                curr = [int(n) for n in curr[1:]]
            else:
                curr = [int(n) for n in curr]
            DEM.append(curr)
        
        line = lines[18]
        curr = line.replace("[", "").replace("]", "").replace("\"", "")
        curr = curr.split()
        MASTER.append(curr[1:])
        
        for line in lines[6:8]:
            curr = line.split()
            MASTER.append(float(curr[1]))
            
    return MASTER
        
master = run()

CPROD = master[0]
CSTOCK = master[1]
FSTOCK = master[2]
ISTOCK = master[3]
PNAME = master[4]
CADD, CRED = master[5], master[6]





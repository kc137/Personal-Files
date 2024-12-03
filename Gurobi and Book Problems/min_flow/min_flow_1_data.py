nodes_dict = {
    "SOURCE" : 1, 
    "D1" : 2, 
    "D2" : 3, 
    "D3" : 4, 
    "D4" : 5, 
    "rail-C1" : 6, 
    "road-C1" : 7, 
    "rail-C2" : 8, 
    "road-C2" : 9, 
    "rail-C3" : 10, 
    "road-C3" : 11, 
    "C1" : 12, 
    "C2" : 13, 
    "C3" : 14, 
    "SINK" : 15
    }

arcs = []

with open("e2_minflow.dat") as data:
    
    raw_lines = data.read().splitlines()
    
    for line in raw_lines[:24]:
        curr = line.replace("A: ", "").replace("[", "").replace("]", "").replace("\"", "")
        curr = curr.split()
        arcs.append((nodes_dict[curr[2]], nodes_dict[curr[3]]))

arcs_cap = {arc : (0, 200) for arc in arcs}

arcs_cap[(1, 2)] = (0, 50)
arcs_cap[(1, 3)] = (0, 40)
arcs_cap[(1, 4)] = (0, 35)
arcs_cap[(1, 5)] = (0, 65)
arcs_cap[(3, 6)] = (10, 50)
arcs_cap[(4, 10)] = (10, 50)
arcs_cap[(5, 8)] = (10, 50)
arcs_cap[(5, 10)] = (10, 50)

costs = {arc : 0 for arc in arcs}

costs[(2, 7)] = 12
costs[(2, 9)] = 11
costs[(3, 6)] = 12
costs[(3, 7)] = 14
costs[(4, 9)] = 9
costs[(4, 10)] = 4
costs[(4, 11)] = 5
costs[(5, 8)] = 11
costs[(5, 9)] = 14
costs[(5, 10)] = 10
costs[(5, 11)] = 14


min_q = 180
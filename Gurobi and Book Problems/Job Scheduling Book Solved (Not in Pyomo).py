jobs = {1 : {"duration" : 6, "due" : 8, "flow" : 6}, 
        2 : {"duration" : 4, "due" : 4, "flow" : 10}, 
        3 : {"duration" : 5, "due" : 12, "flow" : 15}, 
        4 : {"duration" : 8, "due" : 16, "flow" : 23}}

dues, currdue = 0, []
done = []
idxes = []

left, total = 4, 4

x = [[0 for i in range(6)] for i in range(6)]

for i in range(1, total + 1):
    x[i][left] = jobs[4]["flow"] - jobs[i]["due"]
    idxes.append((i, x[i][left]))

left -= 1
done.append(min(idxes, key = lambda x : x[1])[0])
dues += min(idxes, key = lambda x : x[1])[1]

while left:
    currdue = []
    idxes = []

    for i in range(1, total + 1):
        if done[-1] != i:
            if i not in done:
                if (jobs[4]["flow"] - sum(jobs[k]["duration"] for k in done) 
                          + dues - jobs[i]["due"]) > dues:
                    x[i][left] = (jobs[4]["flow"] - sum(jobs[k]["duration"] for k in done) 
                              + dues - jobs[i]["due"])
                    idxes.append((i, x[i][left]))
                    currdue.append(x[i][left])
                else:
                    idxes.append((i, dues))
                    currdue.append(x[i][left])
    if len(set(currdue)) == 1:
        for i in idxes:
            done.append(i[0])
        print("Over and Result is\nDues =", dues)
        left = 0
    else:
        left -= 1
        done.append(min(idxes, key = lambda x : x[1])[0])
        dues = min(idxes, key = lambda x : x[1])[1]
    print("Machine Order", done)
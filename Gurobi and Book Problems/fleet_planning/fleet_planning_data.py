
cm = [[] for _ in range(6)]
contr = [3, 4, 5]
initial_stock = 200
demands = [430, 410, 440, 390, 425, 450]
costs = {3 : 1700, 
         4 : 2200, 
         5 : 2600}

for dur in contr:
    cm[0].append((dur, 1))

for i in range(1, len(cm)):
    j = i - 1
    for d, m in cm[j]:
        if d + m - 1 > i:
            cm[i].append((d, m))
    for c in contr:
        if 6 - i >= c:
            cm[i].append((c, i+1))


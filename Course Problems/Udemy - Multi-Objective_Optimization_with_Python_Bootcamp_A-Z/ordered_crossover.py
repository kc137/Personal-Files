"""
Ordered Crossover
"""

x1 = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
x2 = [9, 7, 0, 2, 8, 1, 4, 3, 5, 6]

cx1 = [0 for _ in range(len(x1))]
cx2 = [0 for _ in range(len(x2))]

i1, i2 = 3, 6

in1 = [0 for _ in range(len(x1))]
in2 = [0 for _ in range(len(x2))]

for v in range(i1, i2 + 1):
    cx1[v] = x2[v]
    cx2[v] = x1[v]
    in1[x2[v]] = 1
    in2[x1[v]] = 1

print(cx1, cx2)

idx1, idx2 = i2+1, i2+1

for i in range(len(x1)):
    if not in1[x1[(i2 + 1 + i) % len(x1)]]:
        cx1[idx1] = x1[(i2 + 1 + i) % len(x1)]
        in1[x1[(i2 + 1 + i) % len(x1)]] = 1
        idx1 = (idx1 + 1) % len(x1)
    
    if not in2[x2[(i2 + 1 + i) % len(x2)]]:
        cx2[idx2] = x2[(i2 + 1 + i) % len(x2)]
        in2[x2[(i2 + 1 + i) % len(x2)]] = 1
        idx2 = (idx2 + 1) % len(x2)



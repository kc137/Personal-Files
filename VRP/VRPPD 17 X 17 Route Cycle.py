route_ans_V1 = [('C1', 'C3'), ('C3', 'C11'), ('C11', 'C17'), ('C15', 'C1'), ('C17', 'C15')]
route_ans_V2 = [('C1', 'C14'), ('C12', 'C13'), ('C13', 'C1'), ('C14', 'C16'), ('C16', 'C12')]
route_ans_V3 = [('C1', 'C2'), ('C2', 'C5'), ('C4', 'C7'), ('C5', 'C4'), ('C7', 'C1')]
route_ans_V4 = [('C1', 'C8'), ('C6', 'C10'), ('C8', 'C9'), ('C9', 'C6'), ('C10', 'C1')]

route_V1 = [route_ans_V1[0]]
route_V2 = [route_ans_V2[0]]
route_V3 = [route_ans_V3[0]]
route_V4 = [route_ans_V4[0]]

while len(route_V1) < len(route_ans_V1):
    for c1, c2 in route_ans_V1:
        if c1 == route_V1[-1][1]:
            route_V1.append((c1, c2))

while len(route_V2) < len(route_ans_V2):
    for c1, c2 in route_ans_V2:
        if c1 == route_V2[-1][1]:
            route_V2.append((c1, c2))

while len(route_V3) < len(route_ans_V3):
    for c1, c2 in route_ans_V3:
        if c1 == route_V3[-1][1]:
            route_V3.append((c1, c2))

while len(route_V4) < len(route_ans_V4):
    for c1, c2 in route_ans_V4:
        if c1 == route_V4[-1][1]:
            route_V4.append((c1, c2))
            
print(route_V1)
print(route_V2)
print(route_V3)
print(route_V4)
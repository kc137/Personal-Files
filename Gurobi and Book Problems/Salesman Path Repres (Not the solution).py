paths = [(1, 17), (2, 14), (3, 12), (4, 5), (5, 15), (6, 13), (7, 16), (8, 9), (9, 4),
         (10, 11), (11, 2), (12, 1), (13, 10), (14, 3), (15, 7), (16, 6), (17, 8)]

travels = [1]

tfromp, ttop = True, True

fromp = {key : 0 for key in range(1, 18)}
top = {key : 0 for key in range(1, 18)}

for p in paths:
    fromp[p[0]] += (p[1])
    top[p[1]] += (p[0])

while len(travels) < (len(paths)):
    currkey = travels[-1]
    travels.append(fromp[travels[-1]])
    
# travels.append(paths[0][0])
print(travels)

print("\nThe salesman route will be\n")

for city in travels:
    if city == travels[0]:
        print(f"{city}", end = " ")
    else:
        print(f"--> {city}", end = " ")
print(f"--> {1}", end = " ")
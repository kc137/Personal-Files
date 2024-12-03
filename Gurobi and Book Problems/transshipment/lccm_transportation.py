from heapq import heapify, heappush, heappop

grid = [[3, 1, 7, 4], [2, 6, 5, 9], [8, 3, 3, 2]]  # table
supply = [300, 400, 500]  # supply
demand = [250, 350, 400, 200]  # demand

sum_dem = sum(demand)
sum_sup = sum(supply)

R, C = len(grid), len(grid[0])

heap_data = []
heapify(heap_data)

for r in range(R):
    for c in range(C):
        heappush(heap_data, (grid[r][c], -abs(supply[r] - demand[c]), r, c))

lcm_sol = 0

supply_track = set()
demand_track = set()

while sum_dem > 0 and sum_sup > 0:
    cost, allocate, r, c = heappop(heap_data)
    if supply[r] <= demand[c] and r not in supply_track:
        lcm_sol += grid[r][c]*supply[r]
        goods = supply[r]
        supply[r] -= goods
        demand[c] -= goods
        # print(supply, demand)
        sum_sup -= goods
        sum_dem -= goods
        supply_track.add(r)
    elif demand[c] <= supply[r] and c not in demand_track:
        lcm_sol += grid[r][c]*demand[c]
        goods = demand[c]
        supply[r] -= goods
        demand[c] -= goods
        # print(supply, demand)
        sum_dem -= goods
        sum_sup -= goods
        demand_track.add(c)

print(f"The solution of the Transportation Problem using LCM : {lcm_sol}")



"""
Tie Case : 
    grid = [[11, 13, 17, 14], [16, 18, 14, 10], [21, 24, 13, 10]]  # table
    supply = [250, 300, 400]  # supply
    demand = [200, 225, 275, 250]  # demand
    
Improved from Online : 
    grid = [[6,2,14,8], [4,12,10,18], [16,6,6,4]]  # table
    supply = [150, 200, 250]  # supply
    demand = [125, 175, 200, 100]  # demand
"""
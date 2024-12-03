def get_subtours(sol):
    subtours = []
    N = len(sol)
    remaining_nodes = [1 for _ in range(N)]
    left = N
    while left > 0:
        subtour = []
        subtours.append(subtour)
        for i in range(N):
            if remaining_nodes[i]:
                start = i + 1
                break
        
        while True:

            subtour.append(start)
            if remaining_nodes[start - 1]:
                remaining_nodes[start - 1] -= 1
                left -= 1
            
            next_node = next((j for (i, j) in sol if i == start and sol[i, j] >= 0.9), None)
            
            if not next_node or not remaining_nodes[next_node - 1]:
                break
            
            start = next_node
            
    return subtours

sol_valid = {(1, 5): 1.0, (2, 6): 1.0, (3, 4): 1.0, (4, 3): 1.0, (5, 7): 1.0, (6, 2): 1.0, (7, 1): 1.0}

print(get_subtours(sol_valid))

"""
{(1, 7): 1.0, (2, 6): 1.0, (3, 2): 1.0, (4, 3): 1.0, (5, 1): 1.0, (6, 5): 1.0, (7, 4): 1.0}
"""

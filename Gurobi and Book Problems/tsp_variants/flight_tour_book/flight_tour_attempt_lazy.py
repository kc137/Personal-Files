def find_subtours(sol):
    """
    Function to find subtours in a solution of the Traveling Salesman Problem (TSP).

    Parameters:
        sol (dict): Solution dictionary representing the TSP solution. The keys are tuples (i, j) representing edges,
                    and the values are binary variables indicating if the edge is selected in the solution.
    Returns:
        subtours (list): List of subtours found in the solution.
    """

    subtours = []  # List to store subtours
    remaining_nodes = list(range(1, len(sol) + 1))  # List of remaining nodes to be visited

    while len(remaining_nodes) > 0:
        subtour = []  # List to store a subtour
        subtours.append(subtour)  # Add the subtour to the list of subtours

        start = remaining_nodes[0]  # Start the subtour from the first remaining node

        while True:
            subtour.append(start)  # Add the current node to the subtour

            if start in remaining_nodes:
                remaining_nodes.remove(start)  # Remove the visited node from the remaining nodes

            next_node = next((j for (i, j), value in sol.items() if i == start and value > 0.5), None)

            # Find the next node in the solution that is connected to the current node and has not been visited yet
            # The value 0.5 is used as a threshold to consider an edge selected in the solution

            if next_node is None or next_node not in remaining_nodes:
                break  # If there is no next node or the next node has already been visited, end the subtour

            start = next_node  # Move to the next node in the subtour

    return subtours

soll = {(1, 1): None, (1, 2): -0.0, (1, 3): -0.0, (1, 4): -0.0, (1, 5): 1.0, (1, 6): -0.0, (1, 7): 0.0, (2, 1): -0.0, (2, 2): None, (2, 3): -0.0, (2, 4): -0.0, (2, 5): -0.0, (2, 6): 1.0, (2, 7): -0.0, (3, 1): -0.0, (3, 2): -0.0, (3, 3): None, (3, 4): 1.0, (3, 5): -0.0, (3, 6): -0.0, (3, 7): 0.0, (4, 1): -0.0, (4, 2): -0.0, (4, 3): 1.0, (4, 4): None, (4, 5): -0.0, (4, 6): -0.0, (4, 7): 0.0, (5, 1): 0.0, (5, 2): 0.0, (5, 3): -0.0, (5, 4): -0.0, (5, 5): None, (5, 6): 0.0, (5, 7): 1.0, (6, 1): -0.0, (6, 2): 1.0, (6, 3): -0.0, (6, 4): -0.0, (6, 5): 0.0, (6, 6): None, (6, 7): -0.0, (7, 1): 1.0, (7, 2): -0.0, (7, 3): 0.0, (7, 4): 0.0, (7, 5): -0.0, (7, 6): -0.0, (7, 7): None}

sol_valid = {k : soll[k] 
             for k in soll if soll[k] and soll[k] >= 0.9}

print(find_subtours(sol_valid))

"""
while True:
    solution = mdl.solve(log_output=True)  # Solve the TSP problem
    if solution is None:
        print("No solution found")  # Print a message if no solution is found
        break
    
    sol = solution.get_value_dict(x, keep_zeros=False)  # Get the solution as a dictionary
    subtours = find_subtours(sol)  # Find subtours in the solution
    print("The subtours are:", subtours)  # Print the subtours
    
    if len(subtours) > 1:  # If there are more than one subtour
        for subtour in subtours:
            if len(subtour) < Nodes:  # If the subtour is not the full tour
                mdl.add_constraint(mdl.sum(x[i, j] for i in subtour for j in subtour if i != j) <= len(subtour) - 1)
                # Add a constraint to eliminate the subtour by limiting the total number of edges within the subtour
    else:
        break  # Break the loop if there is only one subtour or no subtour
    
print(solution)"""
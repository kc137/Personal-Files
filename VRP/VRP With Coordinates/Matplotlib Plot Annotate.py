import matplotlib.pyplot as plt
import numpy as np

# Create a list of node names and coordinates
node_names = ["A", "B", "C", "D", "E"]
node_coordinates = np.array([[0, 0], [1, 0], [1, 1], [0, 1], [0.5, 0.5]])

# Plot the nodes
plt.plot(node_coordinates[:, 0], node_coordinates[:, 1], "o")

# Add the node names to the plot
for i, name in enumerate(node_names):
    plt.annotate(name, (node_coordinates[i, 0], node_coordinates[i, 1]))

# Show the plot
plt.show()
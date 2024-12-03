import matplotlib.pyplot as plt

# Plotting the depot
depot_x, depot_y = 0, 0
plt.plot(depot_x, depot_y, 'ro', markersize=10, label='Depot')

# Plotting the customers
customer_x = [10, -10, 20, 15, -20]  # Example coordinates
customer_y = [20, -30, 30, 0, -30]  # Example coordinates
plt.scatter(customer_x, customer_y, c='b', marker='D', label='Customers')

# Plotting the routes
route_x = [[0, 10, 20, 15, 0], [0, -10, -20, 0]]  # Example route coordinates
route_y = [[0, 20, 30, 0, 0], [0, -30, -30, 0]]  # Example route coordinates

for x, y in zip(route_x, route_y):
    plt.plot(x, y, 'r--', linewidth=1)

# Customize the plot
plt.xlabel('X-axis')
plt.ylabel('Y-axis')
plt.title('Vehicle Routing Problem')
plt.legend()

# Display the plot
plt.show()

for rx, ry in zip(route_x, route_y):
    print((rx, ry))
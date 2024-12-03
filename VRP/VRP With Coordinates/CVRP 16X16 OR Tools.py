"""Capacited Vehicles Routing Problem (CVRP)."""

from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp


def create_data_model():
    """Stores the data for the problem."""
    data = {}
    data['distance_matrix'] = [[0, 26, 61, 61, 59, 35, 31, 37, 57, 72, 13, 43, 35, 28, 14, 65],
     [26, 0, 35, 39, 40, 14, 5, 10, 36, 46, 25, 38, 45, 5, 14, 39],
     [61, 35, 0, 15, 24, 27, 32, 26, 19, 11, 60, 63, 78, 33, 49, 4],
     [61, 39, 15, 0, 10, 27, 37, 32, 6, 21, 64, 72, 84, 35, 52, 17],
     [59, 40, 24, 10, 0, 27, 40, 35, 6, 31, 64, 76, 86, 36, 52, 27],
     [35, 14, 27, 27, 27, 0, 15, 13, 23, 38, 37, 51, 59, 9, 26, 31],
     [31, 5, 32, 37, 40, 15, 0, 6, 35, 42, 28, 36, 47, 8, 18, 35],
     [37, 10, 26, 32, 35, 13, 6, 0, 30, 36, 35, 41, 53, 10, 24, 29],
     [57, 36, 19, 6, 6, 23, 35, 30, 0, 26, 60, 71, 81, 32, 49, 22],
     [72, 46, 11, 21, 31, 38, 42, 36, 26, 0, 71, 70, 87, 44, 60, 7],
     [13, 25, 60, 64, 64, 37, 28, 35, 60, 71, 0, 31, 24, 29, 11, 64],
     [43, 38, 63, 72, 76, 51, 36, 41, 71, 70, 31, 0, 23, 43, 33, 65],
     [35, 45, 78, 84, 86, 59, 47, 53, 81, 87, 24, 23, 0, 50, 34, 81],
     [28, 5, 33, 35, 36, 9, 8, 10, 32, 44, 29, 43, 50, 0, 17, 37],
     [14, 14, 49, 52, 52, 26, 18, 24, 49, 60, 11, 33, 34, 17, 0, 53],
     [65, 39, 4, 17, 27, 31, 35, 29, 22, 7, 64, 65, 81, 37, 53, 0]]
    
    data['demands'] = [0, 26, 27, 16, 25, 18, 29, 24, 21, 27, 31, 21, 36, 25, 36, 21]
    data['vehicle_capacities'] = [100, 100, 100, 100]
    data['num_vehicles'] = 4
    data['depot'] = 0
    return data


def print_solution(data, manager, routing, solution):
    """Prints solution on console."""
    print(f'Objective: {solution.ObjectiveValue()}')
    total_distance = 0
    total_load = 0
    for vehicle_id in range(data['num_vehicles']):
        index = routing.Start(vehicle_id)
        plan_output = 'Route for vehicle {}:\n'.format(vehicle_id)
        route_distance = 0
        route_load = 0
        while not routing.IsEnd(index):
            node_index = manager.IndexToNode(index)
            route_load += data['demands'][node_index]
            plan_output += ' {0} Load({1}) -> '.format(node_index, route_load)
            previous_index = index
            index = solution.Value(routing.NextVar(index))
            route_distance += routing.GetArcCostForVehicle(
                previous_index, index, vehicle_id)
        plan_output += ' {0} Load({1})\n'.format(manager.IndexToNode(index),
                                                 route_load)
        plan_output += 'Distance of the route: {}m\n'.format(route_distance)
        plan_output += 'Load of the route: {}\n'.format(route_load)
        print(plan_output)
        total_distance += route_distance
        total_load += route_load
    print('Total distance of all routes: {}m'.format(total_distance))
    print('Total load of all routes: {}'.format(total_load))


def main():
    """Solve the CVRP problem."""
    # Instantiate the data problem.
    data = create_data_model()

    # Create the routing index manager.
    manager = pywrapcp.RoutingIndexManager(len(data['distance_matrix']),
                                           data['num_vehicles'], data['depot'])

    # Create Routing Model.
    routing = pywrapcp.RoutingModel(manager)


    # Create and register a transit callback.
    def distance_callback(from_index, to_index):
        """Returns the distance between the two nodes."""
        # Convert from routing variable Index to distance matrix NodeIndex.
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return data['distance_matrix'][from_node][to_node]

    transit_callback_index = routing.RegisterTransitCallback(distance_callback)

    # Define cost of each arc.
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)


    # Add Capacity constraint.
    def demand_callback(from_index):
        """Returns the demand of the node."""
        # Convert from routing variable Index to demands NodeIndex.
        from_node = manager.IndexToNode(from_index)
        return data['demands'][from_node]

    demand_callback_index = routing.RegisterUnaryTransitCallback(
        demand_callback)
    routing.AddDimensionWithVehicleCapacity(
        demand_callback_index,
        0,  # null capacity slack
        data['vehicle_capacities'],  # vehicle maximum capacities
        True,  # start cumul to zero
        'Capacity')

    # Setting first solution heuristic.
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)
    search_parameters.local_search_metaheuristic = (
        routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH)
    search_parameters.time_limit.FromSeconds(1)

    # Solve the problem.
    solution = routing.SolveWithParameters(search_parameters)

    # Print solution on console.
    if solution:
        print_solution(data, manager, routing, solution)
    else:
        print("Bye bye")


if __name__ == '__main__':
    main()
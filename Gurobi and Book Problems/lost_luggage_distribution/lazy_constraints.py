import time
from itertools import cycle

import numpy as np
from scipy.spatial.distance import pdist, squareform
import matplotlib.pyplot as plt
import matplotlib as mpl
import networkx as nx
import pyomo.environ as pyo
from pyomo.opt import SolverFactory
from pyomo.contrib.appsi.solvers.highs import Highs

np.random.seed(42)

N = 10
demands = np.random.randint(1, 10, size=N)
demands[0] = 0

demands = [0, 1, 1, 2, 4, 2, 4, 8, 8, 1, 2, 1, 2, 4, 4, 8, 8]

capacity = 15
n_vehicles = 4

coordinates = np.random.rand(N, 2)
# distances = squareform(pdist(coordinates, metric="euclidean"))
distances = [
        # fmt: off
      [0, 548, 776, 696, 582, 274, 502, 194, 308, 194, 536, 502, 388, 354, 468, 776, 662],
      [548, 0, 684, 308, 194, 502, 730, 354, 696, 742, 1084, 594, 480, 674, 1016, 868, 1210],
      [776, 684, 0, 992, 878, 502, 274, 810, 468, 742, 400, 1278, 1164, 1130, 788, 1552, 754],
      [696, 308, 992, 0, 114, 650, 878, 502, 844, 890, 1232, 514, 628, 822, 1164, 560, 1358],
      [582, 194, 878, 114, 0, 536, 764, 388, 730, 776, 1118, 400, 514, 708, 1050, 674, 1244],
      [274, 502, 502, 650, 536, 0, 228, 308, 194, 240, 582, 776, 662, 628, 514, 1050, 708],
      [502, 730, 274, 878, 764, 228, 0, 536, 194, 468, 354, 1004, 890, 856, 514, 1278, 480],
      [194, 354, 810, 502, 388, 308, 536, 0, 342, 388, 730, 468, 354, 320, 662, 742, 856],
      [308, 696, 468, 844, 730, 194, 194, 342, 0, 274, 388, 810, 696, 662, 320, 1084, 514],
      [194, 742, 742, 890, 776, 240, 468, 388, 274, 0, 342, 536, 422, 388, 274, 810, 468],
      [536, 1084, 400, 1232, 1118, 582, 354, 730, 388, 342, 0, 878, 764, 730, 388, 1152, 354],
      [502, 594, 1278, 514, 400, 776, 1004, 468, 810, 536, 878, 0, 114, 308, 650, 274, 844],
      [388, 480, 1164, 628, 514, 662, 890, 354, 696, 422, 764, 114, 0, 194, 536, 388, 730],
      [354, 674, 1130, 822, 708, 628, 856, 320, 662, 388, 730, 308, 194, 0, 342, 422, 536],
      [468, 1016, 788, 1164, 1050, 514, 514, 662, 320, 274, 388, 650, 536, 342, 0, 764, 194],
      [776, 868, 1552, 560, 674, 1050, 1278, 742, 1084, 810, 1152, 274, 388, 422, 764, 0, 798],
      [662, 1210, 754, 1358, 1244, 708, 480, 856, 514, 468, 354, 844, 730, 536, 194, 798, 0],
        # fmt: on
    ]
# distances = np.round(distances, decimals=4)

# Model

model = pyo.ConcreteModel()

# Sets

model.V = pyo.Set(initialize=range(len(demands)))
model.A = pyo.Set(initialize=[(i, j) for i in model.V for j in model.V if i != j])
model.K = pyo.Set(initialize=range(n_vehicles))

# Params

model.Q = pyo.Param(initialize=capacity)
# model.c = pyo.Param(model.A, initialize={(i, j): distances[i, j] for (i, j) in model.A})
model.c = pyo.Param(model.A, initialize={(i, j): distances[i-1][j-1] for (i, j) in model.A})
model.q = pyo.Param(model.V, initialize={i: d for (i, d) in enumerate(demands)})

# Variables

model.x = pyo.Var(model.A, model.K, within=pyo.Binary)
model.y = pyo.Var(model.V, model.K, within=pyo.Binary)

# Constraints

def arcs_in(model, i):
    if i == model.V.first():
        return sum(model.x[:, i, :]) == len(model.K)
    else:
        return sum(model.x[:, i, :]) == 1.0


def arcs_out(model, i):
    if i == model.V.first():
        return sum(model.x[i, :, :]) == len(model.K)
    else:
        return sum(model.x[i, :, :]) == 1.0


def vehicle_assignment(model, i, k):
    return sum(model.x[:, i, k]) == model.y[i, k]


def comp_vehicle_assignment(model, i, k):
    return sum(model.x[i, :, k]) == model.y[i, k]


def capacity_constraint(model, k):
    return sum(model.y[i, k] * model.q[i] for i in model.V) <= model.Q


def subtour_elimination(model, S, Sout, h, k):
    nodes_out = sum(model.x[i, j, k] for i in S for j in Sout)
    return model.y[h, k] <= nodes_out


model.arcs_in = pyo.Constraint(model.V, rule=arcs_in)
model.arcs_out = pyo.Constraint(model.V, rule=arcs_out)
model.vehicle_assignment = pyo.Constraint(model.V, model.K, rule=vehicle_assignment)
model.comp_vehicle_assignment = pyo.Constraint(model.V, model.K, rule=comp_vehicle_assignment)
model.capacity_constraint = pyo.Constraint(model.K, rule=capacity_constraint)
model.subtour_elimination = pyo.ConstraintList()

# Objective

model.obj = pyo.Objective(
    expr=sum(
        model.x[i, j, k] * model.c[i, j]
        for (i, j) in model.A
        for k in model.K
    ),
    sense=pyo.minimize,
)

def find_arcs(model):
    arcs = []
    for i, j in model.A:
        for k in model.K:
            if np.isclose(model.x[i, j, k].value, 1, atol=1e-1):
                arcs.append((i, j))
    return arcs


def find_subtours(arcs):
    G = nx.DiGraph(arcs)
    subtours = list(nx.strongly_connected_components(G))
    return subtours


def eliminate_subtours(model, subtours):
    proceed = False
    for S in subtours:
        if 0 not in S:
            proceed = True
            Sout = {i for i in model.V if i not in S}
            for h in S:
                for k in model.K:
                    model.subtour_elimination.add(subtour_elimination(model, S, Sout, h, k))
    return proceed


def _solve_step(model, solver, verbose=True):
    sol = solver.solve(model)
    arcs = find_arcs(model)
    subtours = find_subtours(arcs)
    if verbose:
        print(f"Current subtours: {subtours}")
    time.sleep(0.1)
    proceed = eliminate_subtours(model, subtours)
    return sol, proceed 


def solve(model, solver, verbose=True):
    proceed = True
    while proceed:
        sol, proceed = _solve_step(model, solver, verbose=verbose)
    return sol

solver = SolverFactory("cplex", heuristics="on")
# solver.set_callback("ste", subtour_elimination)

sol = solve(model, solver)

def find_tours(model):
    tours = []
    for k in model.K:
        node = 0
        tours.append([0])
        while True:
            for j in model.V:
                if (node, j) in model.A:
                    if np.isclose(model.x[node, j, k].value, 1):
                        node = j
                        tours[-1].append(node)
                        break
            if node == 0:
                break
    return tours

tours = find_tours(model)
print(tours)

"""
[[0, 14, 1, 10, 15, 0], [0, 2, 5, 4, 16, 0], [0, 11, 3, 7, 6, 0], [0, 12, 13, 8, 9, 0]]
"""
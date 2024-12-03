import pyomo.environ as pyo
from pyomo.opt import SolverFactory

# Model

model = pyo.ConcreteModel()

# Data

model.nodes = pyo.RangeSet(1, 18)

predecessors = {
    1: [],
    2: [1],
    3: [2],
    4: [2],
    5: [3],
    6: [4, 5],
    7: [4],
    8: [6],
    9: [4, 6],
    10: [4],
    11: [6],
    12: [9],
    13: [7],
    14: [2],
    15: [4, 14],
    16: [8, 11, 14],
    17: [12],
    18: [17]
}

durations = [2, 16, 9, 8, 10, 6, 2, 2, 9, 5, 3, 2, 1, 7, 4, 3, 9, 1]

sequence = []

for node in predecessors:
    for task in predecessors[node]:
        sequence.append((task, node))

# Variables

model.start = pyo.Var(model.nodes, within = pyo.NonNegativeReals)
start = model.start

# Constraints

model.start_time_cons = pyo.ConstraintList()

for pre, n in sequence:
    model.start_time_cons.add(
        start[pre] + durations[pre-1] <= start[n]
        )

# Objective Function

def obj_fn(model):
    return start[model.nodes.at(-1)]
model.obj = pyo.Objective(rule = obj_fn, sense = pyo.minimize)

# Solution

sol = SolverFactory("cplex")
res = sol.solve(model)

# Printing the Solution

print(res)

for task in model.nodes:
    print(f"Start time and end-time of {task} : [{start[task]()}, {start[task]() + durations[task-1]}]")


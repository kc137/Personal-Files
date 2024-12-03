import pyomo.environ as pyo, matplotlib.pyplot as plt, matplotlib
from pyomo.opt import SolverFactory

matplotlib.use('TkAgg') 

# Creating Model

model = pyo.ConcreteModel()
M = 180

NJ = 3
NM = 3
TASKS = 8

# Sets

model.m = pyo.RangeSet(1, NM)
model.j = pyo.RangeSet(1, NJ)
model.t = pyo.RangeSet(1, TASKS - 1)

# Parameters

durations_list = [
    [45, 20, 12], 
    [0, 10, 17], 
    [10, 34, 28]
    ]
model.durations = pyo.Param(model.m, model.j, 
                            within = pyo.Any, 
                            initialize = {
                                (i, j) : durations_list[i-1][j-1] 
                                for i in model.m 
                                for j in model.j
                                })
durations = model.durations

order_list = [[1, 3], [2, 1, 3], [3, 1, 2]]
model.order = pyo.Param(model.j, within = pyo.Any, 
                        initialize = {
                            j : order_list[j-1] for j in model.j
                            })
order = model.order

order_disj_list = [
    [1, 2, 3], 
    [2, 3], 
    [1, 2, 3]
    ]
model.order_disj = pyo.Param(model.m, within = pyo.Any, 
                             initialize = {
                                 m : order_disj_list[m-1] 
                                 for m in model.m
                                 })
order_disj = model.order_disj

# Variables

model.start = pyo.Var(model.m, model.j, within = pyo.NonNegativeReals)
start = model.start

model.finish = pyo.Var(within = pyo.NonNegativeReals, bounds = (0, M))
finish = model.finish

model.y = pyo.Var(model.t, within = pyo.Binary)
y = model.y

# Constratints

def completion_time(model, j):
    return start[order[j][-1], j] + durations[order[j][-1], j] <= finish
model.c1 = pyo.Constraint(model.j, rule = completion_time)

# def conjunctions(model, j, m):
#     if m <= 2:
#         return start[order[j][m-1], j] + durations[order[j][m-1], j] <= start[order[j][m], j]
# model.c2 = pyo.Constraint(model.j, model.m, rule = conjunctions)

model.conjunctions = pyo.ConstraintList()

for m in model.m:
    for j in range(1, len(order[m]) + 1):
        if j == len(order[m]):
            continue
        model.conjunctions.add(start[order[m][j-1], m] + durations[order[m][j-1], m] <= start[order[m][j], m])
        
model.disjunctions = pyo.ConstraintList()

y_len = 1
for m in model.m:
    for j in range(len(order_disj[m])):
        if j >= len(order_disj[m]) - 1:
            continue
        for k in range(j, len(order_disj[m])):
            if k >= len(order_disj[m]) - 1:
                continue
            model.disjunctions.add(start[m, order_disj[m][j]] + durations[m, order_disj[m][j]] <= start[m, order_disj[m][k+1]] + M*y[y_len])
            model.disjunctions.add(start[m, order_disj[m][k+1]] + durations[m, order_disj[m][k+1]] <= start[m, order_disj[m][j]] + M*(1 - y[y_len]))
            y_len += 1

# Objective Function

def obj_fn(model):
    return finish
model.obj = pyo.Objective(rule = obj_fn, sense = pyo.minimize)

# Solution

sol = SolverFactory("cplex")
res = sol.solve(model)

print(res)

for m in model.m:
    for j in model.j:
        if start[m, j]() != None:
            print(f"for-{[m,j]} = {round(start[m,j]())}, {round(start[m,j]()) + durations[m, j]}")
            
# Visualizing the Solution

op_table, empty = {m : [] for m in model.m}, {m : [] for m in model.m}

for m in model.m:
    for j in model.j:
        if start[m, j]() != None:
            op_table[m].append((round(start[m, j]()), round(start[m, j]()) 
                                + durations[m, j], j))
    op_table[m].sort()

for m in model.m:
    for i in range(len(op_table[m]) - 1):
        if i == 0 and op_table[m][i][0] != 0:
            empty[m].append((0, op_table[m][i][0]))
        elif op_table[m][i][1] != op_table[m][i+1][0]:
            empty[m].append((op_table[m][i][1], op_table[m][i+1][0]))

colors = ["blue", "green", "yellow"]

paper_colors = {
    m : colors[m-1] for m in model.m
    }

fig, gnt = plt.subplots(figsize=(10, 10))
plt.figure(1)

gnt.set_xlim(0, 100)
gnt.set_ylim(0, 48)

gnt.set_xlabel("Time (min.)", fontsize = 15)
gnt.set_ylabel("Machine", fontsize = 15)

yticks = [(36//NM)*i for i in range(NM, 0, -1)]
gnt.set_yticks(yticks)
gnt.set_yticklabels(["M" + str(m) for m in range(1, NM+1)], fontsize = 15)

for m in model.m:
    gnt.broken_barh([(x, y-x) for x, y, j in op_table[m]], 
                    [yticks[m-1]-3, 6], 
                    facecolors = [paper_colors[m]], 
                    edgecolor = "black")
    for i, (x, y, j) in enumerate(op_table[m]):
        gnt.text(x = (x + y)/2, 
                 y = yticks[m-1], 
                 s = f"Paper-{j}", 
                 ha = "center", 
                 va = "center", 
                 color = "white", 
                 fontsize = 10)

# gnt.legend("Paper-1")

plt.show()

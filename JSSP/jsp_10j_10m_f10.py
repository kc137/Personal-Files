import pyomo.environ as pyo
from pyomo.opt import SolverFactory
from jsp_10j_10m_f10_data import machine_sequence, processing_times

model = pyo.ConcreteModel()

M = 2000

# Sets and Parameters

model.j = pyo.RangeSet(1, 10)
model.m = pyo.RangeSet(1, 10)
model.t = pyo.RangeSet(1, model.j.at(-1)*model.m.at(-1)*4 + 50)

durations_list = processing_times
model.durations = pyo.Param(model.m, model.j, 
                            within = pyo.Any, 
                            initialize = {
                                (i, j) : durations_list[i-1][j-1] 
                                for i in model.m 
                                for j in model.j
                                })
durations = model.durations

order_list = machine_sequence
model.order = pyo.Param(model.j, within = pyo.Any, 
                        initialize = {
                            j : order_list[j-1] for j in model.j
                            })
order = model.order

order_disj_list = [
    [n for n in model.j] for _ in model.m]
model.order_disj = pyo.Param(model.m, within = pyo.Any, 
                             initialize = {
                                 m : order_disj_list[m-1] 
                                 for m in model.m
                                 })
order_disj = model.order_disj

# Variables

model.start = pyo.Var(model.j, model.m, 
                      within = pyo.NonNegativeReals)
model.y = pyo.Var(model.t, within = pyo.Binary)
model.makespan = pyo.Var(within = pyo.NonNegativeReals)

# Constraints

def completion_time(model, j):
    return model.start[order[j][-1], j] + durations[order[j][-1], j] <= model.makespan
model.c1 = pyo.Constraint(model.j, rule = completion_time)

model.conjunctions = pyo.ConstraintList()

for m in model.m:
    for j in range(1, len(order[m]) + 1):
        if j == len(order[m]):
            continue
        model.conjunctions.add(model.start[order[m][j-1], m] + durations[order[m][j-1], m] <= model.start[order[m][j], m])
        
model.disjunctions = pyo.ConstraintList()

# y_len = 1
# for m in model.m:
#     for j in range(len(order_disj[m])):
#         if j >= len(order_disj[m]) - 1:
#             continue
#         for k in range(j, len(order_disj[m])):
#             if k >= len(order_disj[m]) - 1:
#                 continue
#             model.disjunctions.add(model.start[m, order_disj[m][j]]
#                                     + processing_times[m-1][order_disj[m][j]-1]
#                                     <= model.start[m, order_disj[m][k+1]] + M*model.y[y_len])
#             model.disjunctions.add(model.start[m, order_disj[m][k+1]]
#                                     + processing_times[m-1][order_disj[m][k+1]-1]
#                                     <= model.start[m, order_disj[m][j]] + M*(1 - model.y[y_len]))
#             y_len += 1

y_len = 1
for m in model.m:
    for j in model.j:
        if j >= model.j.at(-1):
            continue
        for k in range(model.j.at(j), model.j.at(-1)):
            if k >= model.j.at(-1):
                continue
            model.disjunctions.add(model.start[m, order_disj[m][j-1]]
                                    + processing_times[m-1][order_disj[m][j-1]-1]
                                    <= model.start[m, order_disj[m][k]] + M*model.y[y_len])
            model.disjunctions.add(model.start[m, order_disj[m][k]]
                                    + processing_times[m-1][order_disj[m][k]-1]
                                    <= model.start[m, order_disj[m][j-1]] + M*(1 - model.y[y_len]))
            y_len += 1


# Objective Function

def obj_fn(model):
    return model.makespan
model.obj = pyo.Objective(rule = obj_fn, sense = pyo.minimize)

# Solution

sol = SolverFactory("cplex")
sol.options["timelimit"] = 20
res = sol.solve(model)

# Printing Solution

print(f"Total Makespan for 10-J, 10-M : {model.obj()} min.")

# with open("results.txt", "w") as result:
#     for j in model.j:
#         for m in model.m:
#             result.write(f"[{j}, {m}] : [{model.start[j, m]()}, {model.start[j, m]() + processing_times[j-1][m-1]}], ")
#         result.write("\n")

# with open("disj.txt", "w") as disj:
#     model.disjunctions.pprint(disj)

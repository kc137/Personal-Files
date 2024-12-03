import pyomo.environ as pyo, pandas as pd
from pyomo.opt import SolverFactory

incompatibilities = set()

with open("9. exam_scheduling.dat") as data:
    lines = data.read().splitlines()
    
for line in lines:
    curr = line.replace("INCOMP: ", "")\
               .replace("\"", "")\
               .replace("(", "")\
               .replace(")", "")\
               .replace("1", "")\
               .replace("[", "")\
               .replace("]", "")
    curr = curr.split()
    for i in range(0, len(curr) - 1, 2):
        if (curr[i+1], curr[i]) not in incompatibilities:
            incompatibilities.add((curr[i], curr[i+1]))

"""
8:00–10:00, 10:15–12:15, 14:00–16:00, and 16:15–18:15
"""
start_times = {1 : "8:00", 
               2 : "10:15", 
               3 : "14:00", 
               4 : "16:15", 
               5 : "8:00", 
               6 : "10:15", 
               7 : "14:00", 
               8 : "16:15"}

end_times = {1 : "10:00", 
             2 : "12:15", 
             3 : "16:00", 
             4 : "18:15", 
             5 : "10:00", 
             6 : "12:15", 
             7 : "16:00", 
             8 : "18:15"}

# Model

model = pyo.ConcreteModel()

# Sets

model.subjects = pyo.Set(initialize = ["DA","NA","C++","SE","PM","J","GMA","LP","MP","S","DSE"])
subjects = model.subjects

model.times = pyo.RangeSet(1, 8)
times = model.times

# Variables

model.exam = pyo.Var(subjects, times, within = pyo.Binary)
exam = model.exam

# Constraints

def exam_once(model, s):
    return pyo.quicksum(exam[s, t] 
                        for t in times) == 1
model.c1 = pyo.Constraint(subjects, rule = exam_once)

def incompatibility_cons(model, e1, e2, t):
    return exam[e1, t] + exam[e2, t] <= 1
model.c2 = pyo.Constraint(incompatibilities, times, rule = incompatibility_cons)

expr = pyo.quicksum(exam[s, t] 
                    for s in subjects 
                    for t in times)
model.obj = pyo.Objective(expr = 100, sense = pyo.maximize)

# Solution

sol = SolverFactory("cplex")
res = sol.solve(model)

# Printing the Solution

times_dict = {1 : "8:00-10:00", 
              2 : "10:15-12:15", 
              3 : "14:00-16:00", 
              4 : "16:15-18:15"}

df_dict = {
    "8:00-10:00" : {"Day-1" : [], 
                    "Day-2" : []}, 
    "10:15-12:15" : {"Day-1" : [], 
                     "Day-2" : []}, 
    "14:00-16:00" : {"Day-1" : [], 
                     "Day-2" : []}, 
    "16:15-18:15" : {"Day-1" : [], 
                     "Day-2" : []}, 
        }

df_dict = {
    "8:00-10:00" : [[], []], 
    "10:15-12:15" : [[], []], 
    "14:00-16:00" : [[], []], 
    "16:15-18:15" : [[], []], 
        }

for s in subjects:
    for t in times:
        if exam[s, t]() and exam[s, t]() >= 0.9:
            # print(f"exam[{s}, {t}] = {exam[s, t]()}")
            if t <= 4:
                df_dict[times_dict[t]][0].append(s)
                print(f"Subject-{s} is scheduled for examination on Day-1 from {start_times[t]} to {end_times[t]}")
            else:
                df_dict[times_dict[t-4]][1].append(s)
                print(f"Subject-{s} is scheduled for examination on Day-2 from {start_times[t]} to {end_times[t]}")

print(df_dict)

for t in df_dict:
    for i in range(len(df_dict[t])):
        to_replace = df_dict[t][i][:]
        df_dict[t][i] = ", ".join(to_replace) if to_replace else "-"

print(df_dict)

df = pd.DataFrame(df_dict, index = ["Day-1", "Day-2"])
"""
Also
df = pd.DataFrame.from_dict(df_dict)
df.index.rename(["Day-1", "Day-2"])
"""

writer = pd.ExcelWriter("res.xlsx") # df.to_excel("res.xlsx")
df.to_excel(writer)

for col in df:
    col_length = max(df[col].astype(str).map(len).max(), len(str(col)) + 2)
    col_idx = df.columns.get_loc(col)
    writer.sheets["Sheet1"].set_column(col_idx, col_idx, col_length)

writer.close()


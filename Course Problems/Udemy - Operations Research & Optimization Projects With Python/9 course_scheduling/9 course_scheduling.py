import pyomo.environ as pyo, pandas as pd, math, numpy as np, warnings
from pyomo.opt import SolverFactory
from datetime import datetime, timedelta

warnings.filterwarnings("ignore")

file_name = "Small_data"
data = pd.ExcelFile(f"{file_name}.xlsx")

courses = data.parse(0, parse_dates = True)
courses = courses.set_index(["Course", "Section"])

rooms = data.parse(1)
rooms = rooms.set_index("Room")

rooms_all = data.parse(3) if file_name == "Small_data" else data.parse(1)
rooms_all = rooms_all.set_index("Room")

criteria = 79
courses_small = courses.loc[courses.loc[:, "Reg Count"] < 0.9*criteria]
courses_big = courses.loc[courses.loc[:, "Reg Count"] >= 0.9*criteria]

rooms_small = rooms.loc[rooms.Size < criteria, :]
rooms_big = rooms.loc[rooms.Size >= criteria, :]

total_slots = 14 if file_name == "Small_data" else 28

# Model

model = pyo.ConcreteModel()

# Sets and Params

model.I = pyo.Set(initialize = courses.index)
I = model.I

model.J = pyo.Set(initialize = rooms.index)
J = model.J

model.K = pyo.Set(initialize = ["M", "T", "W", "H", "F", "S", "U"])
K = model.K

model.L = pyo.Set(initialize = range(0, total_slots))
L = model.L

Ki = courses.loc[:, "First Days"]

S = courses.loc[:, "Reg Count"]

C = rooms.Size

def change_type_uid(item):
    try:
        return str(int(item))
    except:
        return ""

UIDs = courses.loc[:, "First Instructor UID"].apply(change_type_uid)

# Convert time Difference into 30 min slots

U2 = pd.to_datetime(courses.loc[:, "First End Time"].astype(str))

U1 = pd.to_datetime(courses.loc[:, "First Begin Time"].astype(str))
U = ((U2 - U1).apply(timedelta.total_seconds)/1800).apply(math.ceil)

utilization_rate = sum([float(U[i]*len(Ki[i])*S[i]) / 
                        float(rooms_all.Size[courses.loc[:, "First Room"][i]]) 
                        if courses.loc[:, "First Room"][i] in rooms_all.index 
                        else 0.6 
                        for i in I])

print(f"Utilization before optimization : {utilization_rate}")

# Variables

# Binary variable whether the course is assigned to each room at each time slot
# of each day

model.x = pyo.Var(I, J, K, L, within = pyo.Binary)
x = model.x

model.u = pyo.Var(I, J, K, within = pyo.Binary)
u = model.u

# Constraints

# Class capacity constraint
model.c1 = pyo.ConstraintList()

for i in I:
    for j in J:
        for k in Ki[i][:1]:
            for l in L:
                model.c1.add(
                    x[i, j, k, l]*S[i] <= C[j]
                    )
            
# for i in I:
    # print(Ki[i])
    # for k in Ki[i][:1]:
        # print(k, k[:1])
        
# Day of Week Constraint
model.c2 = pyo.ConstraintList()

for i in I:
    for k in K:
        if k not in Ki[i]:
            model.c2.add(
                pyo.quicksum(x[i, j, k, l] 
                             for j in J 
                             for l in L) == 0
                )
        else:
            model.c2.add(
                pyo.quicksum(x[i, j, k, l] 
                             for j in J 
                             for l in L) == U[i]
                )

# One Course Constraint
model.c3 = pyo.ConstraintList()

for j in J:
    for k in K:
        for l in L:
            model.c3.add(
                pyo.quicksum(x[i, j, k, l] 
                             for i in I) <= 1
                )
    
# Unique Room Constraint
model.c4 = pyo.ConstraintList()

for i in I:
    for j in J:
        for k in Ki[i]:
            for l in L:
                model.c4.add(
                    x[i, j, k, l] <= u[i, j , k]
                    )
            model.c4.add(
                pyo.quicksum(x[i, j, k, l] for l in L) <= U[i]*u[i, j, k] 
                )

# Consecutive Slots Constraint
model.c5 = pyo.ConstraintList()

for i in I:
    for j in J:
        for k in Ki[i][:1]:
            for l in L:
                if l + U[i] - 1 < len(L) - 1:
                    for m in range(l + U[i], len(L)):
                        model.c5.add(
                            x[i, j, k, l] + x[i, j, k, m] <= 1
                            )

# Same instructor constraint
model.c6 = pyo.ConstraintList()

for k in K:
    for l in L:
        for uid in np.unique(UIDs.values[UIDs.values != ""]):
            I_uid_boolean = (UIDs == uid)
            I_uid = I[I_uid_boolean]
            I_uid_day_boolean = [True if k in Ki[i] else False for i in I_uid]
            I_uid_day = I_uid[I_uid_day_boolean]
            if sum(I_uid_day_boolean) > 1:
                model.add(pyo.quicksum(x[i,j,k,l] for i in I_uid_day for j in J) <= 1)
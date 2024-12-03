import pyomo.environ as pyo, pandas as pd, gurobipy as gp, sys
from pyomo.opt import SolverFactory

class Technician:
    
    def __init__(self, name, cap, depot):
        self.name = name
        self.cap = cap
        self.depot = depot
    
    def __str__(self):
        return f"Technician : {self.name}\nCapacity : {self.cap}\nDepot : {self.depot}"
    

class Job:
    
    def __init__(self, name, priority, duration, coveredBy):
        self.name = name
        self.priority = priority
        self.duration = duration
        self.coveredBy = coveredBy
    
    def __str__(self):
        about = f"Job : {self.name}\nPriority : {self.priority}\n"\
            f"Duration : {self.duration}\nCovered by : "
        about += ", ".join([t.name for t in self.coveredBy])
        return about

class Customer:
    
    def __init__(self, name, loc, job, tStart, tEnd, tDue):
        self.name = name
        self.loc = loc
        self.job = job
        self.tStart = tStart
        self.tEnd = tEnd
        self.tDue = tDue
    
    def __str__(self):
        coveredBy = ", ".join([t.name for t in self.job.coveredBy])
        return f"Customer : {self.name}\nLocation : {self.loc}\nJob : {self.job.name}\n"\
            f"Priority : {self.job.priority}\nDuration : {self.job.duration}\n"\
                f"Covered by : {coveredBy}\nStart Time : {self.tStart}\n"\
                    f"End Time : {self.tEnd}\nDue Time : {self.tDue}"

# Read excel workbook

df = pd.read_excel("data.xlsx", sheet_name = "Technicians")
df = df.rename(columns = {df.columns[0] : "name", df.columns[1] : "cap", df.columns[2] : "depot"})

df1 = df.drop(df.columns[3:], axis = 1).drop(df.index[[0, 1]])

# Create Technician Objects

technicians = [Technician(*row) for row in df1.itertuples(index = False, name = None)]

# Read Job Data

jobs = []
for j in range(3, len(df.columns)):
    coveredBy = [tec for i, tec in enumerate(technicians) if df.iloc[2+i, j] == 1]
    curr_job = Job(df.iloc[2:, j].name, df.iloc[0, j], df.iloc[1, j], coveredBy)
    jobs.append(curr_job)

# Read Location Data

df_locations = pd.read_excel("data.xlsx", sheet_name = "Locations", index_col = 0)

# Extract locations and initialize distance dictionary

locations = df_locations.index
dist = {(l, l) : 0 for l in locations}

for i, l1 in enumerate(locations):
    for j, l2 in enumerate(locations):
        if i < j:
            dist[l1, l2] = df_locations.iloc[i, j]
            dist[l2, l1] = dist[l1, l2]

# Read Customer Data

df_customers = pd.read_excel("data.xlsx", sheet_name = "Customers")

customers = []
for i, c in enumerate(df_customers.iloc[:, 0]):
    job_name = df_customers.iloc[i, 2]
    
    # Find the corresponding job object
    job_match = next((job for job in jobs if job.name == job_name), None)
    
    if job_match:
        # Create Customer object using corresponding job object
        curr_customer = Customer(c, df_customers.iloc[i, 1], job_match, 
                                 *df_customers.iloc[i, 3:])
        customers.append(curr_customer)

priority = {j.name : j.job.priority for j in customers}

def solve_trs(technicians, customers, dist):
    
    K = [k.name for k in technicians]
    C = [cust.name for cust in customers]
    J = [cust.loc for cust in customers]
    L = list(df_locations.index)
    D = list(set(tech.depot for tech in technicians))
    cap = {tech.name : tech.cap for tech in technicians}
    loc = {cust.name : cust.loc for cust in customers}
    depot = {tech.name : tech.depot for tech in technicians}
    canCover = {cust.name : [k.name for k in cust.job.coveredBy] for cust in customers}
    dur = {cust.name : cust.job.duration for cust in customers}
    tStart = {cust.name : cust.tStart for cust in customers}
    tEnd = {cust.name : cust.tEnd for cust in customers}
    tDue = {cust.name : cust.tDue for cust in customers}
    priority = {cust.name : cust.job.priority for cust in customers}
    
    # Pyomo Model
    model = pyo.ConcreteModel()
    
    # Variables
    
    # Customer-Technician Assignment
    model.x = pyo.Var(C, K, within = pyo.Binary)
    x = model.x
    
    # Technicial Assignment
    model.u = pyo.Var(K, within = pyo.Binary)
    u = model.u
    
    # Route Assignment to Technician
    
    model.y = pyo.Var(L, L, K, within = pyo.Binary)
    y = model.y
    
    model.ub_y = pyo.ConstraintList()
    # for k in technicians:
    #     for d in D:
    #         if k.depot != d:
    #             for i in L:
    #                 y[i, d, k.name] = 0
    #                 y[d, i, k.name] = 0
    for k in technicians:
        for d in D:
            if k.depot != d:
                for i in L:
                    model.ub_y.add(y[i, d, k.name] == 0)
                    model.ub_y.add(y[d, i, k.name] == 0)
    
    # Start Time of service
    model.ts = pyo.Var(L, within = pyo.NonNegativeReals, bounds = (0, 600))
    ts = model.ts
    
    # Lateness of service
    model.z = pyo.Var(C, within = pyo.NonNegativeReals)
    z = model.z
    
    # Variables to correct TW Upper and LLs
    model.xa = pyo.Var(C, within = pyo.NonNegativeReals)
    xa = model.xa
    
    model.xb = pyo.Var(C, within = pyo.NonNegativeReals)
    xb = model.xb
    
    # Unassigned Jobs
    model.g = pyo.Var(C, within = pyo.Binary)
    g = model.g
    
    # Constraints
    
    # Technician assigned or unassigned
    
    def assign_tech(model, j):
        return pyo.quicksum(x[j, k] for k in canCover[j]) + g[j] == 1
    model.c1 = pyo.Constraint(C, rule = assign_tech)
    
    # At most one technician
    
    def one_tech(model, j):
        return pyo.quicksum(x[j, k] for k in K) <= 1
    model.c2 = pyo.Constraint(C, rule = one_tech)
    
    # Technician Capacity
    
    def capacity(model, k):
        return (pyo.quicksum(dur[j]*x[j, k] 
                             for j in C) 
                + pyo.quicksum(dist[i, j]*y[i, j, k] 
                               for i in L 
                               for j in L) 
                <= cap[k]*u[k])
    model.c3 = pyo.Constraint(K, rule = capacity)
    
    # Technician Tour
    """
    For each technician and job, we ensure that if the technician is assigned to the job, 
    then the technician must travel to another location (to form a tour).

    """
    
    def tech_tour_1(model, k, j):
        return pyo.quicksum(y[i, loc[j], k] for i in L) == x[j, k]
    model.c4 = pyo.Constraint(K, C, rule = tech_tour_1)
    
    """
    For each technician and job, we ensure that if a technician is assigned to the job, 
    then the technician must travel from another location to the location of the job 
    (to form a tour).
    """
    
    def tech_tour_2(model, k, j):
        return pyo.quicksum(y[loc[j], i, k] for i in L) == x[j, k]
    model.c5 = pyo.Constraint(K, C, rule = tech_tour_2)
    
    # Same Depot
    """
    For each technician and depot, we ensure that a technician, if assigned to any job, 
    must depart from and return to the service center (depot) where the technician is based.
    """
    
    def depot_1(model, k):
        return (pyo.quicksum(y[j, depot[k], k] 
                            for j in J) 
                == u[k])
    model.c6 = pyo.Constraint(K, rule = depot_1)
    
    def depot_2(model, k):
        return (pyo.quicksum(y[depot[k], j, k] 
                            for j in J) 
                == u[k])
    model.c7 = pyo.Constraint(K, rule = depot_2)
    
    # Temporal Relationship
    """
    For each location and job, we ensure the temporal relationship between two 
    consecutive jobs served by the same technician. That is, if a technician  k  
    travels from job  i  to job  j , then the start of the service time at job  j  
    must be no less than the completion time of job  i  plus the travel time 
    from job  i  to job  j .
    """
    
    # For customer locations
    def temporal_cust(model, i, j):
        M = {(i, j) : 600 + dur[i] + dist[loc[i], loc[j]] 
             for i in C 
             for j in C}
        return (ts[loc[j]] >= ts[loc[i]] + dur[i] + dist[loc[i], loc[j]] 
                - M[i, j]*(1 - pyo.quicksum(y[loc[i], loc[j], k] 
                                        for k in K)))
    model.c8 = pyo.Constraint(C, C, rule = temporal_cust)
    
    # For depot locations
    def temporal_depot(model, i, j):
        M = {(i, j) : 600 + dist[i, loc[j]] 
             for i in D 
             for j in C}
        return (ts[loc[j]] >= ts[i] + dist[i, loc[j]] 
                - M[i, j]*(1 - pyo.quicksum(y[i, loc[j], k] 
                                            for k in K)))
    model.c9 = pyo.Constraint(D, C, rule = temporal_depot)
    
    # Time Window Constraints
    
    def tw_a(model, j):
        return ts[loc[j]] + xa[j] >= tStart[j]
    model.c10 = pyo.Constraint(C, rule = tw_a)
    
    def tw_b(model, j):
        return ts[loc[j]] - xb[j] <= tEnd[j]
    model.c11 = pyo.Constraint(C, rule = tw_b)
    
    # Lateness Constraint
    
    def lateness(model, j):
        return z[j] >= ts[loc[j]] + dur[j] - tDue[j]
    model.c12 = pyo.Constraint(C, rule = lateness)
    
    # Objective Function
    M = 6100
    
    def obj_fn(model):
        return (pyo.quicksum(z[j]*priority[j] 
                             for j in C) 
                + pyo.quicksum(0.01 * M * priority[j] * (xa[j] + xb[j]) 
                               for j in C) 
                + pyo.quicksum(M * priority[j] * g[j] 
                               for j in C))
    model.obj = pyo.Objective(rule = obj_fn, sense = pyo.minimize)
    
    # Solution

    sol = SolverFactory("cplex")
    res = sol.solve(model)

    print(res)

    # Assignments
    print("")
    for j in customers:
        if g[j.name]() > 0.5:
            jobStr = "Nobody assigned to {} ({}) in {}".format(j.name,j.job.name,j.loc)
        else:
            for k in K:
                if x[j.name, k]() > 0.5:
                    jobStr = "{} assigned to {} ({}) in {}. Start at t={:.2f}.".format(k,j.name,j.job.name,j.loc,ts[j.loc]())
                    if z[j.name]() > 1e-6:
                        jobStr += " {:.2f} minutes late.".format(z[j.name]())
                    if xa[j.name]() > 1e-6:
                        jobStr += " Start time corrected by {:.2f} minutes.".format(xa[j.name]())
                    if xb[j.name]() > 1e-6:
                        jobStr += " End time corrected by {:.2f} minutes.".format(xb[j.name]())
        print(jobStr)

    
    return model
    
    


trs_m = solve_trs(technicians, customers, dist)









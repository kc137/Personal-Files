import pyomo.environ as pyo, random, numpy as np, matplotlib.pyplot as plt, matplotlib
from pyomo.opt import SolverFactory
from sklearn.cluster import MiniBatchKMeans

matplotlib.use("tkagg")

seed = 7
n_cust = 50000 # Not 50e3
n_candidates = 20
n_facilities = 8
n_clusters = 50
n_gaussians = 10
threshold = 0.99

random.seed(seed)

customers_per_gaussian = np.random.multinomial(n_cust, [1/n_gaussians]*n_gaussians)
customer_locs = []
for i in range(n_gaussians):
    center = (random.random() - 0.5, random.random() - 0.5)
    customer_locs += [(random.gauss(0, 0.1) + center[0], random.gauss(0, 0.1) + center[1]) 
                      for i in range(customers_per_gaussian[i])]

facility_locs = [(random.random() - 0.5, random.random() - 0.5) for i in range(n_candidates)]

# Clustering

kmeans = MiniBatchKMeans(n_clusters = n_clusters, init_size = 3*n_clusters, random_state = seed).fit(customer_locs)
memberships = list(kmeans.labels_)
centroids = list(kmeans.cluster_centers_) # Center point for each cluster
weights = list(np.histogram(memberships, bins = n_clusters)[0]) # No. of customers in each cluster

# Viable customer-store pairings

def dist(loc1, loc2):
    return np.linalg.norm(loc1 - loc2, ord = 2) # Euclidean Distance

pairings = {(facility, cluster) : dist(facility_locs[facility], centroids[cluster]) 
            for facility in range(n_candidates) 
            for cluster in range(n_clusters) 
            if dist(facility_locs[facility], centroids[cluster]) < threshold}
print(f"Number of viable pairings : {len(pairings.keys())}")

# Model

model = pyo.ConcreteModel()

# Sets and Parameters

model.sel = pyo.Set(initialize = range(n_candidates))

model.locs = pyo.Set(initialize = pairings.keys())

# Variables

model.select = pyo.Var(model.sel, within = pyo.Binary)
select = model.select

model.assign = pyo.Var(model.locs, within = pyo.Binary)
assign = model.assign

# Constraints

def facility_limit(model):
    return pyo.quicksum(select[s] for s in model.sel) <= n_facilities
model.c1 = pyo.Constraint(rule = facility_limit)

def assign_limit(model, x, y):
    return assign[x, y] <= select[x]
model.c2 = pyo.Constraint(model.locs, rule = assign_limit)

# def closest_store(model, cluster):
#     return pyo.quicksum(assign[facility, cluster] for facility, cluster in model.locs) == 1
# model.c3 = pyo.Constraint(range(n_clusters), rule = closest_store)

model.closest_store = pyo.ConstraintList()

for cluster in range(n_clusters):
    model.closest_store.add(pyo.quicksum(assign[loc, cluster] 
                                         for loc, cluster1 in model.locs 
                                         if cluster == cluster1) == 1)

# Objective Function

def obj_fn(model):
    return pyo.quicksum(weights[j]*pairings[i, j]*assign[i, j] 
                        for i, j in model.locs)
model.obj = pyo.Objective(rule = obj_fn, sense = pyo.minimize)

# Solution

sol = SolverFactory("cplex")
res = sol.solve(model)

# Printing the Results

print(f"The Solution for the facilities location problem : {model.obj()}")

# Plotting the Solution

plt.figure(figsize = (10, 10), dpi = 200)
plt.scatter(*zip(*customer_locs), c = "gold", s = 0.5)
plt.scatter(*zip(*centroids), c = "red", s = 10)
plt.scatter(*zip(*facility_locs), c = "green", s = 10)
assignments = [p for p in pairings if assign[p]() >= 0.9]
for p in assignments:
    pts = [facility_locs[p[0]], centroids[p[1]]]
    plt.plot(*zip(*pts), c = "Black", linewidth = 0.2)
plt.show()
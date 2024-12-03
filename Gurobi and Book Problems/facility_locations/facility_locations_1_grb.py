import random

import gurobipy as gp
from gurobipy import GRB

import matplotlib.pyplot as plt, matplotlib
import numpy as np
from sklearn.cluster import MiniBatchKMeans

matplotlib.use("tkagg")

# Tested with Gurobi v9.0.0 and Python 3.7.0

seed = 10101
num_customers = 50000
num_candidates = 20
max_facilities = 8
num_clusters = 50
num_gaussians = 10
threshold = 0.99

random.seed(seed)
customers_per_gaussian = np.random.multinomial(num_customers,
                                               [1/num_gaussians]*num_gaussians)
customer_locs = []
for i in range(num_gaussians):
    # each center coordinate in [-0.5, 0.5]
    center = (random.random()-0.5, random.random()-0.5)
    customer_locs += [(random.gauss(0,.1) + center[0], random.gauss(0,.1) + center[1])
                  for i in range(customers_per_gaussian[i])]
# each candidate coordinate in [-0.5, 0.5]
facility_locs = [(random.random()-0.5, random.random()-0.5)
              for i in range(num_candidates)]
print('First customer location:', customer_locs[0])

kmeans = MiniBatchKMeans(n_clusters=num_clusters, init_size=3*num_clusters,
                         random_state=seed).fit(customer_locs)
memberships = list(kmeans.labels_)
centroids = list(kmeans.cluster_centers_) # Center point for each cluster
weights = list(np.histogram(memberships, bins=num_clusters)[0]) # Number of customers in each cluster
print('First cluster center:', centroids[0])
print('Weights for first 10 clusters:', weights[:10])

def dist(loc1, loc2):
    return np.linalg.norm(loc1-loc2, ord=2) # Euclidean distance

pairings = {(facility, cluster): dist(facility_locs[facility], centroids[cluster])
            for facility in range(num_candidates)
            for cluster in range(num_clusters)
            if  dist(facility_locs[facility], centroids[cluster]) < threshold}
print("Number of viable pairings: {0}".format(len(pairings.keys())))

m = gp.Model("Facility location")

# Decision variables: select facility locations
select = m.addVars(range(num_candidates), vtype=GRB.BINARY, name='select')
# Decision variables: assign customer clusters to a facility location
assign = m.addVars(pairings.keys(), vtype=GRB.BINARY, name='assign')

# Deploy Objective Function
# 0. Total distance
obj = gp.quicksum(weights[cluster]
               *pairings[facility, cluster]
               *assign[facility, cluster]
               for facility, cluster in pairings.keys())
m.setObjective(obj, GRB.MINIMIZE)

# 1. Facility limit
m.addConstr(select.sum() <= max_facilities, name="Facility_limit")

# 2. Open to assign
m.addConstrs((assign[facility, cluster] <= select[facility]
             for facility, cluster in pairings.keys()),
            name="Open2assign")

# 3. Closest store
m.addConstrs((assign.sum('*', cluster) == 1
             for cluster in range(num_clusters)),
            name="Closest_store")

# Find the optimal solution
m.optimize()

plt.figure(figsize=(8,8), dpi=150)
plt.scatter(*zip(*customer_locs), c='Pink', s=0.5)
plt.scatter(*zip(*centroids), c='Red', s=10)
plt.scatter(*zip(*facility_locs), c='Green', s=10)
assignments = [p for p in pairings if assign[p].x > 0.5]
for p in assignments:
    pts = [facility_locs[p[0]], centroids[p[1]]]
    plt.plot(*zip(*pts), c='Black', linewidth=0.1)
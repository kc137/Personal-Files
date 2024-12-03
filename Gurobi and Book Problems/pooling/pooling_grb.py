import numpy as np
import pandas as pd
from itertools import product

import gurobipy as gp
from gurobipy import GRB

# tested with Gurobi v9.1.0 and Python 3.7.0

attrs = {'den', 'bnz', 'roz', 'moz'}

sources, cost, supply, content = gp.multidict({
    "s1": [49.2, 6097.56, {'den': 0.82, 'bnz':3, 'roz':99.2,'moz':90.5}],
    "s2": [62.0, 16129, {'den': 0.62, 'bnz':0, 'roz':87.9,'moz':83.5}],
    "s3": [300.0, 500, {'den': 0.75, 'bnz':0, 'roz':114,'moz':98.7}]
})

targets, price, demand, min_tol, max_tol = gp.multidict({
    "t1": [190, 500, {'den': 0.74, 'roz':95,'moz':85}, {'den': 0.79}],
    "t2": [230, 500, {'den': 0.74, 'roz':96,'moz':88}, {'den': 0.79, 'bnz':0.9}],
    "t3": [150, 500, {'den': 0.74, 'roz':91}, {'den': 0.79}]
})

pools, cap = gp.multidict({
    "p1": 1250,
    "p2": 1750
})

# The function `product` deploys the Cartesian product of elements in sets A and B
s2p = set(product(sources, pools))
p2t = set(product(pools, targets))
s2t = {("s1", "t2"),
       ("s2", "t1"),
       ("s2", "t3"),
       ("s3", "t1")}

p_pooling = gp.Model("Pooling")

# Set global parameters
p_pooling.params.nonConvex = 2
p_pooling.params.timelimit = 20 # time limit 

# Declare decision variables

# flow
ik = p_pooling.addVars(s2t, name="Source2Target")
ij = p_pooling.addVars(s2p, name="Source2Pool")
jk = p_pooling.addVars(p2t, name="Pool2Target")
ik["s1","t2"].ub = 750
ik["s3","t1"].ub = 750
# quality
prop = p_pooling.addVars(pools, attrs, name="Proportion")

p_pooling = gp.Model("Pooling")

# Set global parameters
p_pooling.params.nonConvex = 2
p_pooling.params.timelimit = 20 # time limit 

# Declare decision variables

# flow
ik = p_pooling.addVars(s2t, name="s2t")
ij = p_pooling.addVars(s2p, name="s2p")
jk = p_pooling.addVars(p2t, name="p2t")
ik["s1","t2"].ub = 750
ik["s3","t1"].ub = 750
# quality
prop = p_pooling.addVars(pools, attrs, name="Proportion")

# Deploy constraint sets

# 1. Flow conservation
p_pooling.addConstrs((ij.sum('*',j) == jk.sum(j,'*') for j in pools),
                     name="Flow_conservation")
# 2. Source capacity
p_pooling.addConstrs((ij.sum(i,'*') + ik.sum(i,'*') <= supply[i] for i in sources),
                     name="Source_capacity")
# 3. Pool capacity
p_pooling.addConstrs((jk.sum(j,'*') <= cap[j] for j in pools),
                     name="Pool_capacity")
# 4. Target demand
p_pooling.addConstrs((ik.sum('*',k) + jk.sum('*',k) >= demand[k] for k in targets),
                     name="Target_demand")
# 5. Pool concentration
p_pooling.addConstrs((gp.quicksum(content[i][attr]*ij[i,j]
                               for i in sources if (i,j) in s2p)
                      == prop[j,attr]*jk.sum(j,'*') for j in pools for attr in attrs),
                     name="Pool_concentration")
# 6.1 Target (min) tolerances
p_pooling.addConstrs((gp.quicksum(content[i][attr]*ik[i,k]
                               for i in sources if (i,k) in s2t)
                      + gp.quicksum(prop[j,attr]*jk[j,k]
                                 for j in pools if (j,k) in p2t)
                      >= min_tol[k][attr]*(ik.sum('*',k) + jk.sum('*',k))
                      for k in targets for attr in min_tol[k].keys()),
                     name="Target_min_tolerances")
# 6.2 Target (max) tolerances
p_pooling.addConstrs((gp.quicksum(content[i][attr]*ik[i,k]
                               for i in sources if (i,k) in s2t)
                      + gp.quicksum(prop[j,attr]*jk[j,k]
                                 for j in pools if (j,k) in p2t)
                      <= max_tol[k][attr]*(ik.sum('*',k) + jk.sum('*',k))
                      for k in targets for attr in max_tol[k].keys()),
                     name="Target_max_tolerances")



# Deploy Objective Function

# 0. Total profit
obj = gp.quicksum(price[k]*(ik.sum('*',k) + jk.sum('*',k))
               for k in targets) \
- gp.quicksum(cost[i]*(ij.sum(i,'*') + ik.sum(i,'*'))
           for i in sources)
p_pooling.setObjective(obj, GRB.MAXIMIZE)

p_pooling.update()
p_pooling.display()

# # Find the optimal solution
# p_pooling.optimize()
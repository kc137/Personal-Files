import pyomo.environ as pyo, multidict
from pyomo.opt import SolverFactory
from itertools import product

attrs = {'den', 'bnz', 'roz', 'moz'}

md_1 = {
    "s1": [49.2, 6097.56, {'den': 0.82, 'bnz':3, 'roz':99.2,'moz':90.5}],
    "s2": [62.0, 16129, {'den': 0.62, 'bnz':0, 'roz':87.9,'moz':83.5}],
    "s3": [300.0, 500, {'den': 0.75, 'bnz':0, 'roz':114,'moz':98.7}]
}

sources, cost, supply, content = {k for k in md_1}, {}, {}, {}

for k in md_1:
    cost[k] = md_1[k][0]
    supply[k] = md_1[k][1]
    content[k] = md_1[k][2]
    

md_2 = {
    "t1": [190, 500, {'den': 0.74, 'roz':95,'moz':85}, {'den': 0.79}],
    "t2": [230, 500, {'den': 0.74, 'roz':96,'moz':88}, {'den': 0.79, 'bnz':0.9}],
    "t3": [150, 500, {'den': 0.74, 'roz':91}, {'den': 0.79}]
}

targets, price, demand, min_tol, max_tol = {k for k in md_2}, {}, {}, {}, {}

for k in md_2:
    price[k] = md_2[k][0]
    demand[k] = md_2[k][1]
    min_tol[k] = md_2[k][2]
    max_tol[k] = md_2[k][3]

md_3 = {
    "p1": 1250,
    "p2": 1750
}

pools, cap = {k for k in md_3}, {k : md_3[k] for k in md_3}

# The function `product` deploys the Cartesian product of elements in sets A and B
s2p = set(product(sources, pools))
p2t = set(product(pools, targets))
s2t = {("s1", "t2"),
        ("s2", "t1"),
        ("s2", "t3"),
        ("s3", "t1")}

# Model

model = pyo.ConcreteModel()

# Sets and Parameters

# model.s = pyo.Set(initialize = sources)
# model.p = pyo.Set(initialize = pools)
# model.t = pyo.Set(initialize = targets)

# model.s2p = pyo.Set(initialize = sorted(list(product(sources, pools))))
model.s2p = pyo.Set(initialize = sorted(list(product(sources, pools))))

model.p2t = pyo.Set(initialize = sorted(list(product(pools, targets))))

model.s2t = pyo.Set(initialize = sorted(list(s2t)))

# Variables

model.st = pyo.Var(model.s2t, within = pyo.NonNegativeReals)
st = model.st

model.sp = pyo.Var(model.s2p, within = pyo.NonNegativeReals)
sp = model.sp

model.pt = pyo.Var(model.p2t, within = pyo.NonNegativeReals)
pt = model.pt

model.prop = pyo.Var(pools, attrs, within = pyo.NonNegativeReals)
prop = model.prop

model.c1 = pyo.ConstraintList(name = "Flow Conservation")

for p in pools:
    model.c1.add(pyo.quicksum(sp[s, p] for s in sources) == 
                  pyo.quicksum(pt[p, t] for t in targets))

model.c2 = pyo.ConstraintList(name = "Source Capacity")

for s in sources:
    model.c2.add(pyo.quicksum(sp[s, p] for p in pools) + 
                 pyo.quicksum(st[s, t] for sp, t in model.s2t if sp == s) <= supply[s])

model.ub = pyo.ConstraintList()

model.ub.add((0, st["s1", "t2"], 750))
model.ub.add((0, st["s3", "t1"], 750))

model.c3 = pyo.ConstraintList(name = "Pool Capacity")

for p in pools:
    model.c3.add(pyo.quicksum(pt[p, t] for t in targets) <= cap[p])

model.c4 = pyo.ConstraintList(name = "Target Demand")

for t in targets:
    model.c4.add(pyo.quicksum(st[s, t] for s, ti in model.s2t if ti == t) + 
                 pyo.quicksum(pt[p, t] for p, ti in model.p2t if ti == t) >= 
                 demand[t])
    
model.c5 = pyo.ConstraintList(name = "Pool Concentration")

for p in pools:
    for k in attrs:
        model.c5.add(
            pyo.quicksum(content[s][k]*sp[s, p] for s in sources if (s, p) in model.s2p) == 
            prop[p, k]*pyo.quicksum(pt[p, t] for t in targets) + 0.001
            )
"""
0.001 Was the Key here hahahahahah
"""

model.c6 = pyo.ConstraintList(name = "Minimum Tolerance")

for t in targets:
    for k in min_tol[t].keys():
        model.c6.add(
            pyo.quicksum(content[s][k]*st[s, t] for s in sources if (s, t) in model.s2t) + 
            pyo.quicksum(prop[p, k]*pt[p, t] for p in pools if (p, t) in model.p2t) >= 
            min_tol[t][k]*(pyo.quicksum(st[s, t] for s, ti in model.s2t if ti == t) + 
                           pyo.quicksum(pt[p, t] for p, ti in model.p2t if ti == t))
            )

model.c7 = pyo.ConstraintList(name = "Maximum Tolerance")

for t in targets:
    for k in max_tol[t].keys():
        model.c7.add(
            pyo.quicksum(content[s][k]*st[s, t] for s in sources if (s, t) in model.s2t) + 
            pyo.quicksum(prop[p, k]*pt[p, t] for p in pools if (p, t) in model.p2t) <= 
            max_tol[t][k]*(pyo.quicksum(st[s, t] for s, ti in model.s2t if ti == t) + 
                           pyo.quicksum(pt[p, t] for p, ti in model.p2t if ti == t))
            )

# Objective Function

def obj_fn(model):
    
    expr1 = pyo.quicksum(price[t]*st[s, t] 
                        for t in targets 
                        for s, ti in model.s2t if ti == t)
    expr2 = pyo.quicksum(price[t]*pt[p, t] 
                        for t in targets 
                        for p, ti in model.p2t if ti == t)
    expr3 = pyo.quicksum(cost[s]*sp[s, p] 
                        for s in sources 
                        for si, p in model.s2p if si == s)
    expr4 = pyo.quicksum(cost[s]*st[s, t] 
                        for s in sources 
                        for si, t in model.s2t if si == s)
            
    return expr1 + expr2 - expr3 - expr4

model.obj = pyo.Objective(rule = obj_fn, sense = pyo.maximize)

# expr = (-110.0*st["s3","t1"] + 88.0*st["s2","t3"] + 180.8*st["s1","t2"] + 128.0*st["s2","t1"] - 
#         62.0*sp["s2","p2"] - 300.0*sp["s3","p2"] - 49.2*sp["s1","p1"] - 62.0*sp["s2","p1"] - 
#         300.0*sp["s3","p1"] - 49.2*sp["s1","p2"] + 150.0*pt["p2","t3"] + 230.0*pt["p1","t2"] + 
#         190.0*pt["p2","t1"] + 190.0*pt["p1","t1"] + 150.0*pt["p1","t3"] + 230.0*pt["p2","t2"])

# model.obj = pyo.Objective(expr = expr, sense = pyo.maximize)

# Solution

sol = SolverFactory("bonmin")
# sol.options["timelimit"] = 30
res = sol.solve(model)

# Printing the Solution

# print(f"Max Flow to targets : {model.obj()}")
try:
    print(f"Max Profit for Flow to targets : {model.obj()} $.")
except ValueError:
    print("No Feasible Solution.")

# # Solution

# sol = SolverFactory("cplex")
# sol.options["timelimit"] = 20
# res = sol.solve(model)

# Printing the Results

s_t = {(s, t) : 0 for s in sorted(sources) for t in sorted(targets)}

for s in sorted(sources):
    for t in sorted(targets):
        try:
            s_t[(s, t)] = st[s, t]()
        except KeyError:
            s_t[(s, t)] = 0



expr1, expr2 = 0, 0
for t in targets:
    for s, ti in model.s2t:
        for p in pools:
            if ti == t:
                expr1 += price[t]*(st[s, t] + pt[p, t])

for s in sources:
    for p in pools:
        for t in targets:
            for s, ti in model.s2t:
                if ti == t:
                    expr2 += cost[s]*(sp[s, p] + st[s, t])

expr3 = (-110.0*st["s3","t1"] + 88.0*st["s2","t3"] + 180.8*st["s1","t2"] + 128.0*st["s2","t1"] - 
        62.0*sp["s2","p2"] - 300.0*sp["s3","p2"] - 49.2*sp["s1","p1"] - 62.0*sp["s2","p1"] - 
        300.0*sp["s3","p1"] - 49.2*sp["s1","p2"] + 150.0*pt["p2","t3"] + 230.0*pt["p1","t2"] + 
        190.0*pt["p2","t1"] + 190.0*pt["p1","t1"] + 150.0*pt["p1","t3"] + 230.0*pt["p2","t2"])

# print((expr1 - expr2) == expr3)







"""
Profit = 411,530.70 USD
"""

"""
print(230*(st[s1,t2] + pt[p2,t2] + st[s1,t2] + pt[p1,t2]) + 
      190*(st[s2,t1] + pt[p2,t1] + st[s2,t1] + pt[p1,t1] + 
            st[s3,t1] + pt[p2,t1] + st[s3,t1] + pt[p1,t1]) + 
      150*(st[s2,t3] + pt[p2,t3] + st[s2,t3] + pt[p1,t3]) - 
      (300.0*(sp[s1,p2] + st[s1,t2] + sp[s1,p1] + st[s1,t2] + sp[s1,p2] + 
              st[s1,t2] + sp[s1,p1] + st[s1,t2] + sp[s1,p2] + st[s1,t2] 
              + sp[s1,p1] + st[s1,t2]) + 
        300.0*(sp[s2,p2] + st[s2,t1] + sp[s3,p2] + st[s3,t1] + sp[s2,p1] + 
              st[s2,t1] + sp[s3,p1] + st[s3,t1] + sp[s2,p2] + st[s2,t1] + 
              sp[s3,p2] + st[s3,t1] + sp[s2,p1] + st[s2,t1] + sp[s3,p1] + 
              st[s3,t1] + sp[s2,p2] + st[s2,t1] + sp[s3,p2] + st[s3,t1] + 
              sp[s2,p1] + st[s2,t1] + sp[s3,p1] + st[s3,t1]) + 
        300.0*(sp[s2,p2] + st[s2,t3] + sp[s2,p1] + st[s2,t3] + sp[s2,p2] + 
              st[s2,t3] + sp[s2,p1] + st[s2,t3] + sp[s2,p2] + st[s2,t3] + 
              sp[s2,p1] + st[s2,t3])))


(-110.0*st["s3","t1"] + 88.0*st["s2","t3"] + 180.8*st["s1","t2"] + 128.0*st["s2","t1"] +
-62.0*sp["s2","p2"] + -300.0*sp["s3","p2"] + -49.2*sp["s1","p1"] + -62.0*sp["s2","p1"] +
-300.0*sp["s3","p1"] + -49.2*sp["s1","p2"] + 150.0*pt["p2","t3"] + 230.0*pt["p1","t2"]
+ 190.0*pt["p2","t1"] + 190.0*pt["p1","t1"] + 150.0*pt["p1","t3"] + 230.0*pt["p2","t2"])
"""
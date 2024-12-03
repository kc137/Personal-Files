import pyomo.environ as pyo, pandas as pd, numpy as np, networkx as nx, \
    matplotlib.pyplot as plt, seaborn as sns, datetime, matplotlib
from pyomo.opt import SolverFactory

matplotlib.use("tkagg")
    
node_types = pd.read_csv("node_types.csv")

# Load the data on the type of cities and no. of beneficiaries in each camp.

N = set(node_types["Name"])
N_S = set([sup[:-2] for sup in N if sup[-2:] == " S"]) # Suppliers
N_TS = set([th[:-3] for th in N if th[-2:] == "TS"]) # Transit Hubs
N_B = set([bene[:-2] for bene in N if bene[-1:] == "D"])
N = N_S.union(N_TS, N_B)

print(f"There are {len(N)} cities in total."
      f"\nOut of which {len(N_S)}-cities are suppliers."
      f"\n{len(N_B)}-cities are beneficiary camps."
      f"\n{len(N_S.intersection(N_B))}-cities act as both.")

demand = {bene : node_types.set_index("Name").stack().to_dict()[bene + " D", "Demand"] 
          for bene in N_B}

# bar = sns.barplot(x = list(demand), y = [demand[k] for k in demand])
# bar.set_xticklabels(bar.get_xticklabels(), rotation = 40)

"""Next load the data on the transportation links (i.e. directed edges) in the 
transportation network along with the associated travel costs. Store and visualize 
the data during the networkx graph data-structure.
"""

edge_costs = pd.read_csv("edge_costs.csv")
# print(edge_costs.head())

t = edge_costs.set_index(["A", "B"]).tCost.to_dict()
edges = list(t.keys())

G = nx.DiGraph()
G.add_edges_from(edges)
# plt.figure(figsize = (10, 10))
# color_map = ["green" if (i in N_S and i not in N_B) 
#               else "red" if (i in N_B and i not in N_S) 
#               else "blue" if (i in N_B and i in N_S) 
#               else "lightblue" for i in G.nodes()]
# nx.draw(G, pos = nx.kamada_kawai_layout(G), node_color = color_map, 
#         with_labels = True, verticalalignment = "top", horizontalalignment = "right")
#         # node_size = 900, linewidth = 0.25)

# nx.draw_networkx_edge_labels(G, pos = nx.kamada_kawai_layout(G), edge_labels = t)

"""
Next we gather nutritional requirements for each person
"""

nutrient_requirements = pd.read_csv("nutrient_requirements.csv")
# print(nutrient_requirements)

U = nutrient_requirements.columns.values.tolist()
U.remove("Type")

m = {u : nutrient_requirements.to_dict()[u][0] for u in U}
m_df = pd.DataFrame(m, index = [0])

"""
Next we gather nutritional info for foods
"""

food_nutrition = pd.read_csv("food_nutrition.csv")
F = set(food_nutrition["Food"]) # All food types
# v = food_nutrition.set_index("Food")
v = food_nutrition.set_index("Food").stack().to_dict()

df_nutrition = pd.Series(v).reset_index() # Just creating a new DF to display
df_nutrition.columns = ["Food", "Nutrient", "Amount"]
df_nutrition.pivot_table(index = ["Food"], columns = "Nutrient", 
                         values = "Amount", fill_value = 0).reset_index().rename_axis(None, axis = 1)

# Procurement Costs

"""
Procuring food comes at a cost. For this model we will use the mean 
historical food costs (in USD).
"""

df_food_costs = pd.read_csv("food_costs.csv")
p = df_food_costs.set_index(["supplier", "food"])["Mean"].to_dict()
# print(df_food_costs.head())

"""
Finally, the data from 'food_costs.csv' only contains a subset of all food types 
and supplier cities. For the rest of the food types and suppliers, we set their 
procurement costs to be the international average prices derived from the 
'food_internationalprice.csv' as shown below. Due to this limitation in data availability, 
we assume that the prices are constant for these food types and cities.

Aggregating both the datasets and the regressor fit, we can estimate procurement costs 
for a given month and year. Below are the estimated costs for January 2022.
"""

international_food_price = pd.read_csv("food_internationalprice.csv").set_index("Food")["InternationalPrice"].to_dict()
# print(international_food_price.head())
p.update({(i, f) : international_food_price[f] 
          for f in F 
          for i in N_S 
          if (i, f) not in p})
p_unstack = pd.Series(p).unstack()

# Model

model = pyo.ConcreteModel(name = "Food Supply")

# Variables

# Ration size per person for food type f in beneficiary city j
model.r = pyo.Var(F, N_B, within = pyo.NonNegativeReals)
r = model.r

# Amount of food type f purchased in supplier city i
model.s = pyo.Var(F, N_S, within = pyo.NonNegativeReals)
s = model.s

# Amount of food type f transported on the line (i, j)
model.x = pyo.Var(F, edges, within = pyo.NonNegativeReals)
x = model.x

print(f"Total variables : {len(s) + len(r) + len(x)}")

# Constraints

"""
Constraints that ensure nutritional requirements
"""

def nut_req(model, u, j):
    return (m[u], pyo.quicksum(v[f, u]*r[f, j] for f in F), 2*m[u])
model.c1 = pyo.Constraint(U, N_B, rule = nut_req)

"""
Flow constraints to show flow of food from suppliers to beneficiaries
"""

# Example of preceding and succeeding constraints.

delta_minus = {i : set(G.predecessors(i)) for i in N}
delta_plus = {i : set(G.successors(i)) for i in N}

# print(f"Hama can receive food from {delta_minus['Hama']} and supply food to {delta_plus['Hama']}")

def flow_cons(model, f, i):
    if i in N_B and i not in N_S:
        return (pyo.quicksum(x[f, j, i] for j in delta_minus[i]) - 
                pyo.quicksum(x[f, i, j] for j in delta_plus[i])) == demand[i]*r[f, i]
    if i in N_S and i not in N_B:
        return (pyo.quicksum(x[f, i, j] for j in delta_plus[i]) - 
                pyo.quicksum(x[f, j, i] for j in delta_minus[i])) == s[f, i]
    if i in N_S and i in N_B:
        return (pyo.quicksum(x[f, i, j] for j in delta_plus[i]) - 
                pyo.quicksum(x[f, j, i] for j in delta_minus[i])) == s[f, i] - demand[i]*r[f, i]
model.c2 = pyo.Constraint(F, N, rule = flow_cons)

# Objective Function

"""
Goal is to Minimize the total cost incurred in procuring the food from the supplier 
cities and in transporting the food through the network.
"""

def obj_fn(model):
    return (pyo.quicksum(s[f, i]*p[i, f] 
                        for f in F 
                        for i in N_S) 
            +
            pyo.quicksum(x[f, i, j]*t[i, j] 
                         for f in F 
                         for i, j in edges 
                         if i != j))
model.obj = pyo.Objective(rule = obj_fn, sense = pyo.minimize)

# Solution

sol = SolverFactory("cplex")
res = sol.solve(model)

print(f"Total minimized cost in procuring and transporting the food : ${model.obj()}")
# print(res)





import pyomo.environ as pyo, matplotlib.pyplot as plt, matplotlib, \
    seaborn as sns, pandas as pd, gurobipy as gp
from pyomo.opt import SolverFactory
matplotlib.use("tkagg")

df_load_curves = pd.read_csv("demand.csv")
# print(df_load_curves[-5:])

# Select the demand for the chosen day (1-Jul-2011)

df_subset = df_load_curves[(df_load_curves["YEAR"] == 2011) 
                           & (df_load_curves["MONTH"] == 7) 
                           & (df_load_curves["DAY"] == 1)]
d = df_subset.set_index(["HOUR"]).LOAD.to_dict()

H = set(d.keys())

# fig, ax = plt.subplots()
# demand_plot = sns.barplot(x = list(range(1, 25)), y = [d[h] for h in range(1, 25)])
# # demand_plot.set_xticklabels(demand_plot.get_xticklabels())
# demand_plot.set(xlabel = "Hour", ylabel = "Demand (MWH)")
# plt.show()

df_plant_info = pd.read_csv("plant_capacities.csv")

# Set of all power-plants
P = set(df_plant_info["Plant"].unique())

# Plant type for each plant
plant_type = df_plant_info.set_index("Plant").PlantType.to_dict()

# Set of all nuclear plants
P_N = set([i for i in P if plant_type[i] == "NUCLEAR"])

# Fuel type for each plant
fuel_type = df_plant_info.set_index("Plant").FuelType.to_dict()

df_plant_info["capacity"] = df_plant_info["Capacity"]

c = df_plant_info.set_index("Plant").capacity.to_dict()

# capacity_plot = sns.barplot(x = list(c.keys()), y = [c[k] for k in c])
# capacity_plot.tick_params(rotation = 40)
# capacity_plot.set(xlabel = "Plant", ylabel = "Capacity (MWH)")
# plt.show()

# Min limit

m = {plant : 0.8 if plant in P_N else 0.01 for plant in P}

# Ramp up/down speed

r = {plant : 1 if plant in ["BIOMASS", "GAS", "HYDRO", "OIL"] 
     else 0.2 if plant in P_N 
     else 0.25 
     for plant in P}

# Finally we load the costs.

df_fuel_costs = pd.read_csv("fuel_costs.csv")

# Read the fuel costs and transform it from fuel-type to plant-name

f = {fuel : df_fuel_costs[df_fuel_costs["year"] == 2011].T.to_dict()[9][fuel_type[fuel]] 
     for fuel in fuel_type}

# # Plot the fuel-costs

# fuelcost_plot = sns.barplot(x = list(f.keys()), y = [f[k] for k in f])
# fuelcost_plot.tick_params(rotation = 40)
# fuelcost_plot.set(xlabel = "Plant", ylabel = "Fuel cost per MWH ($)")
# plt.show()

# Operaiton Costs

df_oper_costs = pd.read_csv("operating_costs.csv")

o = {fuel : df_oper_costs[df_oper_costs["year"] == 2011].T.to_dict()[9][fuel_type[fuel]] 
     for fuel in fuel_type}

# Startup and Shutdown Costs. Ensures stable power generation schedule

df_startup_costs = pd.read_csv("startup_costs.csv")

s = {fuel : df_startup_costs[df_startup_costs["year"] == 2011].T.to_dict()[9][fuel_type[fuel]] 
     for fuel in fuel_type}

# Assuming the shut-down costs are the same as start-up costs
t = s.copy()

"""
Finally, we load the health costs, which capture the health effects of burning 
too much coal. This data is only available for the three coal plants 
(Bowen, Jack McDonough and Scherer). The health costs are aggregated using a 
variety of environmental factors that depend on the time of the day. 
As a result, these costs are indexed for each hour. See the visualization below 
for health costs for the Bowen power plant to observe that the costs are much 
higher in the evenings than in the mornings.
"""

df_health_costs = pd.read_csv("health_costs.csv")
a = df_health_costs[(df_health_costs["Year"] == 2007) 
                    & (df_health_costs["Day"] == 1)].set_index(
                        ["Plant", "Hour"]).to_dict()["Cost"]
a.update({(p, h) : 0 for p in P for h in H 
         if p not in ['Bowen','Jack McDonough','Scherer']})

# fig, ax = plt.subplots()
# healthcost_plot = sns.barplot(x = list(range(1, 25)), y = [a["Scherer", h] 
#                                                            for h in range(1, 25)])
# healthcost_plot.set(xlabel = "Hour", ylabel = "Health Costs in Scherer ($)")
# plt.show()

# Model

model = pyo.ConcreteModel()

# Variables

# Power generated in each plant at each hour
model.z = pyo.Var(P, H, within = pyo.NonNegativeReals)
z = model.z

# Indicates whether the plant is on for each plant at each hour
model.u = pyo.Var(P, H, within = pyo.Binary)
u = model.u

# Indicates whether the plant is started or not at each hour
model.v = pyo.Var(P, H, within = pyo.Binary)
v = model.v

# Indicates whether the plant is shut-down or not at each hour
model.w = pyo.Var(P, H, within = pyo.Binary)
w = model.w

# Constraints

def meet_demand(model, h):
    return pyo.quicksum(z[p, h] 
                        for p in P) == d[h]
model.c1 = pyo.Constraint(H, rule = meet_demand)

# Maximum and Minimum generation levels

def min_power_gen(model, p, h):
    return z[p, h] >= m[p]*c[p]*u[p, h]
model.c2 = pyo.Constraint(P, H, rule = min_power_gen)

def max_power_gen(model, p, h):
    return z[p, h] <= c[p]*u[p, h]
model.c3 = pyo.Constraint(P, H, rule = max_power_gen)

# Nuclear Plants always on

def nuclear_plant_on(model, p, h):
    return z[p, h] >= m[p]*c[p]
model.c4 = pyo.Constraint(P_N, H, rule = nuclear_plant_on)

# Max Ramp-Up and Ramp-Down

def ramp_up_down(model, p, h):
    if h > 1:
        return (-r[p]*c[p], z[p, h] - z[p, h-1], r[p]*c[p])
    else:
        return pyo.Constraint.Skip
model.c5 = pyo.Constraint(P, H, rule = ramp_up_down)

# If a plant is ON then it must be ON and generate the power

def switch_on(model, p, h):
    return v[p, h] <= u[p, h]
model.c6 = pyo.Constraint(P, H, rule = switch_on)

# If a plant is OFF then it must be OFF and generate no power

def switch_off(model, p, h):
    return w[p, h] <= 1 - u[p, h]
model.c7 = pyo.Constraint(P, H, rule = switch_off)

# Link startup/shutdown variables to on/off variables 
"""(3 possible values: -1, 0, 1)"""

def link_var_cons(model, p, h):
    if h > 1:
        return v[p, h] - w[p, h] == u[p, h] - u[p, h-1]
    else:
        return pyo.Constraint.Skip
model.c8 = pyo.Constraint(P, H, rule = link_var_cons)

# Objective Function

def obj_fn(model):
    return (pyo.quicksum(f[p]*z[p, h] 
                        for p in P 
                        for h in H) 
            + pyo.quicksum(a[p, h]*z[p, h] 
                                for p in P 
                                for h in H) 
            + pyo.quicksum(o[p]*u[p, h] 
                                for p in P 
                                for h in H) 
            + pyo.quicksum(s[p]*v[p, h] 
                                for p in P 
                                for h in H) 
            + pyo.quicksum(t[p]*w[p, h] 
                                for p in P 
                                for h in H))
model.obj = pyo.Objective(rule = obj_fn, sense = pyo.minimize)

# Solution

sol = SolverFactory("cplex")
res = sol.solve(model)

# Printing the Solution

print(res)

















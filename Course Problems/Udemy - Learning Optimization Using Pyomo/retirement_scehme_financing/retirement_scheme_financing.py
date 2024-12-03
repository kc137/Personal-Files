import pyomo.environ as pyo
from pyomo.opt import SolverFactory

model = pyo.ConcreteModel()

bond_info = []
with open("nums.txt") as nums:
    read = nums.read()
    amounts = [int(num) for num in read.splitlines()[0].split(" ")]
    
    for line in read.splitlines()[1:]:
        if not line:
            continue
        bond_info.append([float(num) for num in line.split(" ")])

fixed_rate = 3.2/100

# Sets

model.years = pyo.RangeSet(1, 7)
model.bonds = pyo.RangeSet(1, 3)

# Parameters

model.amounts_req = pyo.Param(model.years, within = pyo.Any, 
                              initialize = {
                                  n : 1000*amounts[n-1] for n in model.years
                                  })
amounts_req = model.amounts_req

model.bond_values = pyo.Param(model.bonds, within = pyo.Any, 
                              initialize = {
                                  n : 1000*bond_info[n-1][0] for n in model.bonds
                                  })
bond_values = model.bond_values

model.bond_interest_rates = pyo.Param(model.bonds, within = pyo.Any, 
                              initialize = {
                                  n : 0.01*bond_info[n-1][1] for n in model.bonds
                                  })
bond_interest_rates = model.bond_interest_rates

model.bond_durations = pyo.Param(model.bonds, within = pyo.Any, 
                              initialize = {
                                  n : bond_info[n-1][2] for n in model.bonds
                                  })
bond_durations = model.bond_durations

# Variables

model.buy = pyo.Var(model.bonds, within = pyo.NonNegativeIntegers)
buy = model.buy

model.invest = pyo.Var(model.years, within = pyo.NonNegativeReals)
invest = model.invest

model.capital = pyo.Var(within = pyo.NonNegativeReals)
capital = model.capital

# Constraints

def investment_equilibrium(model, t):
    if t == 1:
        return (capital - 
                sum(bond_values[b]*buy[b] for b in model.bonds) - 
                invest[t]) == amounts_req[t]
    elif t <= 4:
        return (sum(bond_values[b]*buy[b]*bond_interest_rates[b] 
                    for b in model.bonds) 
                + (1 + fixed_rate)*invest[t-1] 
                - invest[t]) == amounts_req[t]
    elif t <= 6:
        return (sum(bond_values[b]*buy[b]*(1 + bond_interest_rates[b]) 
                    for b in model.bonds 
                    if bond_durations[b] == t-1)
                + sum(bond_values[b]*buy[b]*bond_interest_rates[b] 
                    for b in model.bonds 
                    if bond_durations[b] >= t) 
                + (1 + fixed_rate)*invest[t-1] 
                - invest[t]) == amounts_req[t]
    else:
        return ((sum(bond_values[b]*buy[b]*(1 + bond_interest_rates[b]) 
                    for b in model.bonds 
                    if bond_durations[b] == t-1))  
                 + (1 + fixed_rate)*invest[t-1]) == amounts_req[t]
model.c1 = pyo.Constraint(model.years, rule = investment_equilibrium)

# Objective Function

model.obj = pyo.Objective(expr = capital, sense = pyo.minimize)

# Solution

sol = SolverFactory("cplex")
res = sol.solve(model)

print(res)
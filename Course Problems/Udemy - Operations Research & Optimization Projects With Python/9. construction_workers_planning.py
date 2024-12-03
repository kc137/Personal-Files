import pyomo.environ as pyo
from pyomo.opt import SolverFactory

# Model

model = pyo.ConcreteModel()

# Sets and Params

model.months = pyo.Set(initialize = ["Mar", "Apr", "May", "Jun", "Jul", "Aug"])
months = model.months

req_list = [4, 6, 7, 4, 6, 2]

model.req = pyo.Param(months, initialize = {months.at(m) : req_list[m-1] 
                                            for m in range(1, len(months) + 1)})
req = model.req

arrival = 100
leave = 160
over = 200
under = 200

n_feb = 3 # At the start
n_aug = 3 # At the end

# Variables

# Workers present for current month
model.curr = pyo.Var(months, within = pyo.NonNegativeIntegers)
curr = model.curr

# Workers incoming for current month
model.w_in = pyo.Var(months, within = pyo.NonNegativeIntegers)
w_in = model.w_in

# Workers outgoing for current month
model.w_out = pyo.Var(months, within = pyo.NonNegativeIntegers)
w_out = model.w_out

# Workers overtime
model.w_over = pyo.Var(months, within = pyo.NonNegativeIntegers)
w_over = model.w_over

# Workers req for deficit
model.w_under = pyo.Var(months, within = pyo.NonNegativeIntegers)
w_under = model.w_under

# Constraints

# Initial Balance
expr_1 = curr[months.at(1)] == n_feb + w_in[months.at(1)]
model.c1 = pyo.Constraint(expr = expr_1)

# Final Balance
# curr[months.prev(months.at(-1))]
expr_2 = curr[months.at(-1)] == curr[months.prev(months.at(-1))] + n_aug - w_out[months.at(-1)] + w_in[months.at(-1)]
expr_2 = curr[months.at(-1)] == n_aug + w_out[months.at(-1)]
model.c2 = pyo.Constraint(expr = expr_2)

def intermediate_balance(model, m):
    # , "Aug"
    if m not in ["Mar"]:
        return curr[m] == curr[months.prev(m)] + w_in[m] - w_out[months.prev(m)]
    else:
        return pyo.Constraint.Skip
model.c3 = pyo.Constraint(months, rule = intermediate_balance)

def required_cons(model, m):
    return curr[m] + w_under[m] - w_over[m] == req[m]
model.c4 = pyo.Constraint(months, rule = required_cons)

model.c5 = pyo.ConstraintList()

for m in months:
    model.c5.add(w_in[m] <= 3)
    model.c5.add(w_under[m] <= (1/4)*curr[m] + 0.001)
    model.c5.add(w_out[m] <= (1/3)*curr[m] + 0.001)
# model.c5.add(curr[months.at(1)] == n_feb + w_in[months.at(1)])
# model.c5.add(curr[months.at(-1)] == n_aug + w_out[months.at(-1)])

# Objective Function

def obj_fn(model):
    return pyo.quicksum(arrival*w_in[m] + leave*w_out[m] + over*w_over[m] + under*w_under[m] 
                        for m in months)
model.obj = pyo.Objective(rule = obj_fn, sense = pyo.minimize)

# Solution

sol = SolverFactory("cplex")
res = sol.solve(model)

# Printing the Solution

print(res)

req_res = [0]*6
curr_res = [0]*6
w_in_res = [0]*6
w_out_res = [0]*6
w_over_res = [0]*6
w_under_res = [0]*6

for m in range(len(months)):
    req_res[m] = float(round(req[months.at(m+1)]))
    curr_res[m] = float(round(curr[months.at(m+1)]()))
    w_in_res[m] = float(round(w_in[months.at(m+1)]()))
    w_out_res[m] = float(round(w_out[months.at(m+1)]()))
    w_over_res[m] = float(round(w_over[months.at(m+1)]()))
    w_under_res[m] = float(round(w_under[months.at(m+1)]()))

print(req_res)
print(curr_res)
print(w_in_res)
print(w_out_res)
print(w_over_res)
print(w_under_res)
from pyomo.environ import *
import matplotlib.pyplot as plt

# max 			f1 = X1
# max 			f2 = 3 X1 + 4 X2
# constraints	X1 <= 20
#     			X2 <= 40
# 				5 X1 + 4 X2 <= 200

model = ConcreteModel()

model.X1 = Var(within=NonNegativeReals)
model.X2 = Var(within=NonNegativeReals)

model.C1 = Constraint(expr = model.X1 <= 20)
model.C2 = Constraint(expr = model.X2 <= 40)
model.C3 = Constraint(expr = 5 * model.X1 + 4 * model.X2 <= 200)

model.f1 = Var()
model.f2 = Var()
model.C_f1 = Constraint(expr = model.f1 == model.X1)
model.C_f2 = Constraint(expr = model.f2 == 3 * model.X1 + 4 * model.X2)
model.O_f1 = Objective(expr = model.f1, sense=maximize)
model.O_f2 = Objective(expr = model.f2, sense=maximize)

# max f1 separately
# install glpk solver:  sudo apt-get install glpk-utils
model.O_f2.deactivate()
solver = SolverFactory('glpk')  #'cplex', 'ipopt'
solver.solve(model)

print('( X1 , X2 ) = ( ' + str(value(model.X1)) + ' , ' + str(value(model.X2)) + ' )')
print('f1 = ' + str(value(model.f1)))
print('f2 = ' + str(value(model.f2)))
f2_min = value(model.f2)

# max f2 separately
model.O_f2.activate()
model.O_f1.deactivate()
solver = SolverFactory('glpk')  #'cplex', 'ipopt'
solver.solve(model)

print('( X1 , X2 ) = ( ' + str(value(model.X1)) + ' , ' + str(value(model.X2)) + ' )')
print('f1 = ' + str(value(model.f1)))
print('f2 = ' + str(value(model.f2)))
f2_max = value(model.f2)

# apply augmented $\epsilon$-Constraint
# max   		f1 + delta*s
# constraint 	f2 - s = e
model.O_f1.activate()
model.O_f2.deactivate()

model.del_component(model.O_f1)
model.del_component(model.O_f2)

model.e = Param(initialize=0, mutable=True)
model.delta = Param(initialize=0.00001)
model.slack = Var(within=NonNegativeReals)
model.O_f1 = Objective(expr = model.f1 + model.delta * model.slack, sense=maximize)
model.C_e = Constraint(expr = model.f2 - model.slack == model.e)

n = 100
step = int((f2_max - f2_min) / n)
steps = list(range(int(f2_min),int(f2_max),step)) + [f2_max]

x1_l, x2_l = [], []
f1_l, f2_l = [], []
for i in steps:
    model.e = i
    solver.solve(model)
    x1_l.append(value(model.X1))
    x2_l.append(value(model.X2))
    f1_l.append(value(model.f1))
    f2_l.append(value(model.f2))
    # print(i, value(model.X1), value(model.X2), value(model.f1), value(model.slack), value(model.f2))

fig, (ax1, ax2) = plt.subplots(nrows=1, ncols=2, sharex=True, figsize=(10,4))
edge, = ax1.plot(x1_l,x2_l,'o', markersize=6, markerfacecolor='none', c='b')
shaded = ax1.fill_between(x1_l, x2_l, color='azure', alpha=0.85)
ax1.legend([(edge, shaded)], ['Decision/coordinate space'], loc='best')
ax1.set_xlabel('X1')
ax1.set_ylabel('X2')
ax1.set_xlim((7.5,20.5))
ax1.set_ylim((24,40.5))
ax1.grid(True)

ax2.plot(f1_l, f2_l, 'o-', c='r', label='Pareto optimal front')
ax2.legend(loc='best')
ax2.set_xlabel('Objective function F1')
ax2.set_ylabel('Objective function F2')
ax2.grid(True)
fig.tight_layout()
plt.show()

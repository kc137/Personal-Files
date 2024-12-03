import pyomo.environ as pyo
from pyomo.opt import SolverFactory

days = {1 : "Monday", 2 : "Tuesday", 3 : "Wednesday", 4 : "Thursday", 5 : "Friday", 
        6 : "Saturday", 7 : "Sunday"}

model = pyo.ConcreteModel()
total = 7 # Hours
full = 8
part = 4
full_d, part_d = 15, 10

# Sets

model.i = pyo.RangeSet(1, 7)

workers = {1 : 17, 2 : 13, 3 : 15, 4 : 19, 5 : 14, 6 : 16, 7 : 11}

# Variables

model.x = pyo.Var(model.i, domain = pyo.NonNegativeIntegers)
x = model.x

model.y = pyo.Var(model.i, domain = pyo.NonNegativeIntegers)
y = model.y

# Constraints

# model.C = pyo.ConstraintList()

# for j in model.i:
#     model.C.add(full*sum(x[i] for i in model.i) - x[(j)%total + 1] - x[(j+1)%total + 1] + 
#                 part*sum(y[i] for i in model.i) - y[(j)%total + 1] - y[(j+1)%total + 1] >= workers[j]*8)

# model.C.add(sum(y[i] for i in model.i) <= (1/4)*sum(x[i] + y[i] for i in model.i))

def Cons1(model):
    return (8*sum(x[i] for i in range(1, 6)) + 
            4*sum(y[i] for i in range(1, 6))) >= 14*8

model.C1 = pyo.Constraint(rule = Cons1)

def Cons2(model):
    return (8*sum(x[i] for i in range(2, 7)) + 
            4*sum(y[i] for i in range(2, 7))) >= 16*8

model.C2 = pyo.Constraint(rule = Cons2)

def Cons3(model):
    return (8*sum(x[i] for i in range(3, 8))+ 
            4*sum(y[i] for i in range(3, 8))) >= 11*8

model.C3 = pyo.Constraint(rule = Cons3)

def Cons4(model):
    return (8*(x[1] + sum(x[i] for i in range(4, 8))) + 
            4*(y[1] + sum(y[i] for i in range(4, 8)))) >= 17*8

model.C4 = pyo.Constraint(rule = Cons4)

def Cons5(model):
    return (8*(x[1] + x[2] + sum(x[i] for i in range(5, 8))) + 
            4*(y[1] + y[2] + sum(y[i] for i in range(5, 8))))>= 13*8

model.C5 = pyo.Constraint(rule = Cons5)

def Cons6(model):
    return (8*x[1] + x[2] + x[3] + sum(x[i] for i in range(6, 8)) + 
            4*(y[1] + y[2] + y[3] + sum(y[i] for i in range(6, 8))))>= 15*8

model.C6 = pyo.Constraint(rule = Cons6)

def Cons7(model):
    return (8*(x[7] + sum(x[i] for i in range(1, 5))) + 
            4*(y[7] + sum(y[i] for i in range(1, 5))) >= 19*8)

model.C7 = pyo.Constraint(rule = Cons7)

model.C8 = pyo.Constraint(expr = 0.75*sum(y[i] for i in model.i) <= 0.25*sum(x[i]for i in model.i))
# Objective Function

def Obj_Fn(model):
    return 120*(sum(x[i] for i in model.i)) + 40*(sum(y[i] for i in model.i))
model.Obj = pyo.Objective(rule = Obj_Fn, sense = pyo.minimize)

# Solution

sol = SolverFactory("glpk")
res = sol.solve(model)

fulltimeworkers, parttimeworkers = 0, 0
for i in model.i:
    print(f"Full time Workers on {days[i]} = {x[i]()}")
    print(f"Part time Workers on {days[i]} = {y[i]()}")
    fulltimeworkers += x[i]()
    parttimeworkers += y[i]()
    
print(f"Total cost after minimizing workers will be {model.Obj()}")
print(f"Workers Full Time : {fulltimeworkers}"
      f"\nWorkers Part Time : {parttimeworkers}")
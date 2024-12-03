import pyomo.environ as pyo, gurobipy as gp
from pyomo.opt import SolverFactory

# List of NOR gates 1 to 7.

gates = ['1','2','3','4','5','6','7']

# List of NOR gates 4 to 7.

gates47 = ['4','5','6','7']

# List of rows of the truth-table in the range 1 to 4.

rows = ['1','2','3','4']

# Create a dictionary to capture the value of the external input A and B in the r row of the truth table, for each 
# NOR gate i.

gatesRows, valueA, valueB = gp.multidict({
    ('1','1'): [0,0],
    ('1','2'): [0,1],
    ('1','3'): [1,0],
    ('1','4'): [1,1],
    ('2','1'): [0,0],
    ('2','2'): [0,1],
    ('2','3'): [1,0],
    ('2','4'): [1,1],
    ('3','1'): [0,0],
    ('3','2'): [0,1],
    ('3','3'): [1,0],
    ('3','4'): [1,1],
    ('4','1'): [0,0],
    ('4','2'): [0,1],
    ('4','3'): [1,0],
    ('4','4'): [1,1],
    ('5','1'): [0,0],
    ('5','2'): [0,1],
    ('5','3'): [1,0],
    ('5','4'): [1,1],
    ('6','1'): [0,0],
    ('6','2'): [0,1],
    ('6','3'): [1,0],
    ('6','4'): [1,1],
    ('7','1'): [0,0],
    ('7','2'): [0,1],
    ('7','3'): [1,0],
    ('7','4'): [1,1]
})

gate_dict = {
    "1" : ["2", "3"], 
    "2" : ["4", "5"], 
    "3" : ["6", "7"]
    }

# Model

model = pyo.ConcreteModel()

# Variables

# Decision variables to select NOR Gate-i

model.NOR = pyo.Var(gates, within = pyo.Binary)
NOR = model.NOR

"""
To avoid a trivial solution containing no NOR gates, it is necessary to impose 
a constraint that selects NOR gate 1.
"""

model.nor_1 = pyo.Constraint(expr = NOR["1"] >= 1)

# Variables to decide if external input-A is an input to NOR gate i.
model.inputA = pyo.Var(gates, within = pyo.Binary)
inputA = model.inputA

# Variables to decide if external input-B is an input to NOR gate i.
model.inputB = pyo.Var(gates, within = pyo.Binary)
inputB = model.inputB

# Output decision variables
model.output = pyo.Var(gatesRows, within = pyo.Binary)
output = model.output

"""
For NOR gate-1, the output variables are fixed at the values speecified in 
the truth table
"""

model.output_1 = pyo.ConstraintList()

model.output_1.add(output["1", "1"] <= 0)
model.output_1.add(output["1", "2"] >= 1)
model.output_1.add(output["1", "3"] >= 1)
model.output_1.add(output["1", "4"] <= 0)

# Constraints

# A NOR can only have an external input if it exists

def ext_inputs_A(model, i):
    return NOR[i] >= inputA[i]
model.c1 = pyo.Constraint(gates, rule = ext_inputs_A)

def ext_inputs_B(model, i):
    return NOR[i] >= inputB[i]
model.c2 = pyo.Constraint(gates, rule = ext_inputs_B)

"""
If a NOR gate has one (or two) external inputs leading into it, 
only one (or no) NOR gates can feed into it.
"""

model.NOR_gate = pyo.ConstraintList()

for i in gates[:3]:
    model.NOR_gate.add(pyo.quicksum(NOR[j] 
                                    for j in gate_dict[i]) + inputA[i] + inputB[i] <= 2)
    
"""
The output signal from NOR gate i must be the correct logical function (NOR) 
of the input signals into gate i, if gate i exists.
"""

model.output_signals = pyo.ConstraintList()

for r in rows:
    for i in gates[:3]:
        for j in gate_dict[i]:
            model.output_signals.add(
                output[i, r] + output[j, r] <= 1
                )

model.output_signals_2 = pyo.ConstraintList()

for r in rows:
    for i in gates:
        model.output_signals_2.add(
            valueA[i, r]*inputA[i] + output[i, r] <= 1
            )
        model.output_signals_2.add(
            valueB[i, r]*inputB[i] + output[i, r] <= 1
            )
        
model.output_signals_3 = pyo.ConstraintList()

for r in rows:
    for i in gates47:
        model.output_signals_3.add(
            valueA[i, r]*inputA[i] + valueB[i, r]*inputB[i] + output[i, r] - NOR[i] >= 0
            )

for r in rows:
    for i in gates[:3]:
        for j in gate_dict[i]:
            model.output_signals.add(
                valueA[i, r]*inputA[i] + valueB[i, r]*inputB[i] 
                + pyo.quicksum(output[j, r] for j in gate_dict[i])
                + output[i, r] - NOR[i] >= 0
                )

# Gate and Output signal constraints

def gate_output_cons(model, i, r):
    return NOR[i] - output[i, r] >= 0
model.c3 = pyo.Constraint(gatesRows, rule = gate_output_cons)

# Objective Function

def obj_fn(model):
    return pyo.quicksum(NOR[i] for i in gates)
model.obj = pyo.Objective(rule = obj_fn, sense = pyo.minimize)

# Solution

sol = SolverFactory("cplex")
res = sol.solve(model)

# Printing the Solution

print(res)
for g in gates:
    print(f"NOR-{g} : {NOR[g]()}")







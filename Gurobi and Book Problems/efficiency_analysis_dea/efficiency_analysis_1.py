import pyomo.environ as pyo, gurobipy as gp
from pyomo.opt import SolverFactory

def solve(inp_dmu):
    inattr = ['staff', 'showRoom', 'Population1', 'Population2', 'alphaEnquiries', 'betaEnquiries']
    outattr = ['alphaSales', 'BetaSales', 'profit']

    dmus, inputs, outputs = gp.multidict({
        'Winchester': [{'staff': 7, 'showRoom': 8, 'Population1': 10, 'Population2': 12, 'alphaEnquiries': 8.5, 'betaEnquiries': 4}, {'alphaSales': 2, 'BetaSales': 0.6, 'profit': 1.5}],
        'Andover': [{'staff': 6, 'showRoom': 6, 'Population1': 20, 'Population2': 30, 'alphaEnquiries': 9, 'betaEnquiries': 4.5}, {'alphaSales': 2.3, 'BetaSales': 0.7, 'profit': 1.6}],
        'Basingstoke': [{'staff': 2, 'showRoom': 3, 'Population1': 40, 'Population2': 40, 'alphaEnquiries': 2, 'betaEnquiries': 1.5}, {'alphaSales': 0.8, 'BetaSales': 0.25, 'profit': 0.5}],
        'Poole': [{'staff': 14, 'showRoom': 9, 'Population1': 20, 'Population2': 25, 'alphaEnquiries': 10, 'betaEnquiries': 6}, {'alphaSales': 2.6, 'BetaSales': 0.86, 'profit': 1.9}],
        'Woking': [{'staff': 10, 'showRoom': 9, 'Population1': 10, 'Population2': 10, 'alphaEnquiries': 11, 'betaEnquiries': 5}, {'alphaSales': 2.4, 'BetaSales': 1, 'profit': 2}],
        'Newbury': [{'staff': 24, 'showRoom': 15, 'Population1': 15, 'Population2': 13, 'alphaEnquiries': 25, 'betaEnquiries': 1.9}, {'alphaSales': 8, 'BetaSales': 2.6, 'profit': 4.5}],
        'Portsmouth': [{'staff': 6, 'showRoom': 7, 'Population1': 50, 'Population2': 40, 'alphaEnquiries': 8.5, 'betaEnquiries': 3}, {'alphaSales': 2.5, 'BetaSales': 0.9, 'profit': 1.6}],
        'Alresford': [{'staff': 8, 'showRoom': 7.5, 'Population1': 5, 'Population2': 8, 'alphaEnquiries': 9, 'betaEnquiries': 4}, {'alphaSales': 2.1, 'BetaSales': 0.85, 'profit': 2}],
        'Salisbury': [{'staff': 5, 'showRoom': 5, 'Population1': 10, 'Population2': 10, 'alphaEnquiries': 5, 'betaEnquiries': 2.5}, {'alphaSales': 2, 'BetaSales': 0.65, 'profit': 0.9}],
        'Guildford': [{'staff': 8, 'showRoom': 10, 'Population1': 30, 'Population2': 35, 'alphaEnquiries': 9.5, 'betaEnquiries': 4.5}, {'alphaSales': 2.05, 'BetaSales': 0.75, 'profit': 1.7}],
        'Alton': [{'staff': 7, 'showRoom': 8, 'Population1': 7, 'Population2': 8, 'alphaEnquiries': 3, 'betaEnquiries': 2}, {'alphaSales': 1.9, 'BetaSales': 0.70, 'profit': 0.5}],
        'Weybridge': [{'staff': 5, 'showRoom': 6.5, 'Population1': 9, 'Population2': 12, 'alphaEnquiries': 8, 'betaEnquiries': 4.5}, {'alphaSales': 1.8, 'BetaSales': 0.63, 'profit': 1.4}],
        'Dorchester': [{'staff': 6, 'showRoom': 7.5, 'Population1': 10, 'Population2': 10, 'alphaEnquiries': 7.5, 'betaEnquiries': 4}, {'alphaSales': 1.5, 'BetaSales': 0.45, 'profit': 1.45}],
        'Bridport': [{'staff': 11, 'showRoom': 8, 'Population1': 8, 'Population2': 10, 'alphaEnquiries': 10, 'betaEnquiries': 6}, {'alphaSales': 2.2, 'BetaSales': 0.65, 'profit': 2.2}],
        'Weymouth': [{'staff': 4, 'showRoom': 5, 'Population1': 10, 'Population2': 10, 'alphaEnquiries': 7.5, 'betaEnquiries': 3.5}, {'alphaSales': 1.8, 'BetaSales': 0.62, 'profit': 1.6}],
        'Portland': [{'staff': 3, 'showRoom': 3.5, 'Population1': 3, 'Population2': 20, 'alphaEnquiries': 2, 'betaEnquiries': 1.5}, {'alphaSales': 0.9, 'BetaSales': 0.35, 'profit': 0.5}],
        'Chichester': [{'staff': 5, 'showRoom': 5.5, 'Population1': 8, 'Population2': 10, 'alphaEnquiries': 7, 'betaEnquiries': 3.5}, {'alphaSales': 1.2, 'BetaSales': 0.45, 'profit': 1.3}],
        'Petersfield': [{'staff': 21, 'showRoom': 12, 'Population1': 6, 'Population2': 6, 'alphaEnquiries': 15, 'betaEnquiries': 8}, {'alphaSales': 6, 'BetaSales': 0.25, 'profit': 2.9}],
        'Petworth': [{'staff': 6, 'showRoom': 5.5, 'Population1': 2, 'Population2': 2, 'alphaEnquiries': 8, 'betaEnquiries': 5}, {'alphaSales': 1.5, 'BetaSales': 0.55, 'profit': 1.55}],
        'Midhurst': [{'staff': 3, 'showRoom': 3.6, 'Population1': 3, 'Population2': 3, 'alphaEnquiries': 2.5, 'betaEnquiries': 1.5}, {'alphaSales': 0.8, 'BetaSales': 0.20, 'profit': 0.45}],
        'Reading': [{'staff': 30, 'showRoom': 29, 'Population1': 120, 'Population2': 80, 'alphaEnquiries': 35, 'betaEnquiries': 20}, {'alphaSales': 7, 'BetaSales': 2.5, 'profit': 8}],
        'Southampton': [{'staff': 25, 'showRoom': 16, 'Population1': 110, 'Population2': 80, 'alphaEnquiries': 27, 'betaEnquiries': 12}, {'alphaSales': 6.5, 'BetaSales': 3.5, 'profit': 5.4}],
        'Bournemouth': [{'staff': 19, 'showRoom': 10, 'Population1': 90, 'Population2': 22, 'alphaEnquiries': 25, 'betaEnquiries': 13}, {'alphaSales': 5.5, 'BetaSales': 3.1, 'profit': 4.5}],
        'Henley': [{'staff': 7, 'showRoom': 6, 'Population1': 5, 'Population2': 7, 'alphaEnquiries': 8.5, 'betaEnquiries': 4.5}, {'alphaSales': 1.2, 'BetaSales': 0.48, 'profit': 2}],
        'Maidenhead': [{'staff': 12, 'showRoom': 8, 'Population1': 7, 'Population2': 10, 'alphaEnquiries': 12, 'betaEnquiries': 7}, {'alphaSales': 4.5, 'BetaSales': 2, 'profit': 2.3}],
        'Fareham': [{'staff': 4, 'showRoom': 6, 'Population1': 1, 'Population2': 1, 'alphaEnquiries': 7.5, 'betaEnquiries': 3.5}, {'alphaSales': 1.1, 'BetaSales': 0.48, 'profit': 1.7}],
        'Romsey': [{'staff': 2, 'showRoom': 2.5, 'Population1': 1, 'Population2': 1, 'alphaEnquiries': 2.5, 'betaEnquiries': 1}, {'alphaSales': 0.4, 'BetaSales': 0.1, 'profit': 0.55}],
        'Ringwood': [{'staff': 2, 'showRoom': 3.5, 'Population1': 2, 'Population2': 2, 'alphaEnquiries': 1.9, 'betaEnquiries': 1.2}, {'alphaSales': 0.3, 'BetaSales': 0.09, 'profit': 0.4}]
    })

    # Model

    model = pyo.ConcreteModel()

    # Variables

    model.out = pyo.Var(outattr, within = pyo.NonNegativeReals)
    out = model.out
    
    model.inp = pyo.Var(inattr, within = pyo.NonNegativeReals)
    inp = model.inp
    

    # Constraints

    def efficiency_ratio(model, dmu):
        return (pyo.quicksum(outputs[dmu][o]*out[o] for o in outattr) <= 
                pyo.quicksum(inputs[dmu][i]*inp[i] for i in inattr))
    model.c1 = pyo.Constraint(dmus, rule = efficiency_ratio)
    
    def normalization(model):
        return pyo.quicksum(inputs[inp_dmu][i]*inp[i] for i in inattr) == 1
    model.c2 = pyo.Constraint(rule = normalization)
    
    # Objective Function
    
    def obj_fn(model):
        return pyo.quicksum(outputs[inp_dmu][o]*out[o] for o in outattr)
    model.obj = pyo.Objective(rule = obj_fn, sense = pyo.maximize)
    
    # Solution
    
    sol = SolverFactory("cplex")
    res = sol.solve(model)
    
    # Printing the Solution
    # with open("efficiency_analysis_results.txt", "a") as efal:
        
    #     efal.write(f"{inp_dmu} : \n")
    #     efal.write("\nThe Weights for the Inputs are :\n\n")
        
    #     for ip in inattr:
    #         efal.write(f"{ip} : {round(inp[ip](), 3)}\n")
            
    #     efal.write("\nThe Weights for the Outputs are :\n\n")
        
    #     for op in outattr:
    #         efal.write(f"{op} : {round(out[op](), 3)}\n")
        
    #     output_res = round(model.obj(), 3)
    #     efal.write(f"\nThe maximum efficiency of {inp_dmu} : {output_res}\n\n")
    
    output_res = round(model.obj(), 3)
    
    return output_res

dmus = ['Winchester','Andover','Basingstoke', 'Poole', 'Woking','Newbury','Portsmouth','Alresford','Salisbury','Guildford','Alton','Weybridge', 'Dorchester', 'Bridport', 'Weymouth', 'Portland', 'Chichester', 'Petersfield', 'Petworth', 'Midhurst', 'Reading', 'Southampton', 'Bournemouth', 'Henley', 'Maidenhead', 'Fareham', 'Romsey', 'Ringwood']

efficiency_dmus = {}

for dmu in dmus:
    efficiency_dmus[dmu] = solve(dmu)
    
efficiency_dmus_items = sorted(efficiency_dmus.items(), key = lambda x : x[1])

efficient, inefficient = [], []

for dmu, eff in efficiency_dmus_items:
    if eff < 0.9999:
        inefficient.append(dmu)
    else:
        efficient.append(dmu)
        
print("List of efficient DMUs :\n")
for dmu in efficient:
    print(f"{dmu} with an efficiency of {efficiency_dmus[dmu]}")
    
print("\nList of inefficient DMUs :\n")
for dmu in inefficient:
    print(f"{dmu} with an efficiency of {efficiency_dmus[dmu]}")
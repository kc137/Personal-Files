from pyomo.environ import *
from IPython.display import display
import pandas as pd
    

JOBS = {
    'A': {'release': 2, 'duration': 5, 'due': 10},
    'B': {'release': 5, 'duration': 6, 'due': 21},
    'C': {'release': 4, 'duration': 8, 'due': 15},
    'D': {'release': 0, 'duration': 4, 'due': 10},
    'E': {'release': 0, 'duration': 2, 'due':  5},
    'F': {'release': 8, 'duration': 3, 'due': 15},
    'G': {'release': 9, 'duration': 2, 'due': 22},
}

import pandas as pd
from IPython.display import display
display(pd.DataFrame(JOBS))

# create model
m = ConcreteModel()

# index set to simplify notation
J = list(JOBS.keys())

# decision variables
m.start      = Var(J, domain=NonNegativeReals)
m.makespan   = Var(domain=NonNegativeReals)
m.pastdue    = Var(J, domain=NonNegativeReals)
m.early      = Var(J, domain=NonNegativeReals)

# additional decision variables for use in the objecive
m.ispastdue  = Var(J, domain=Binary)
m.maxpastdue = Var(domain=NonNegativeReals)

# for modeling disjunctive constraints
m.y = Var(J, J, domain=Binary)
BigM = 1000  #  max([JOBS[j]['release'] for j in J]) + sum([JOBS[j]['duration'] for j in J])

m.OBJ = Objective(
    expr = sum([m.pastdue[j] for j in J]),
    sense = minimize
)

m.cons = ConstraintList()
for j in J:
    m.cons.add(m.start[j] >= JOBS[j]['release'])
    m.cons.add(m.start[j] + JOBS[j]['duration'] + m.early[j] == JOBS[j]['due'] + m.pastdue[j])
    m.cons.add(m.pastdue[j] <= m.maxpastdue)
    m.cons.add(m.start[j] + JOBS[j]['duration'] <= m.makespan)
    m.cons.add(m.pastdue[j] <= BigM*m.ispastdue[j])
    for k in J:
        if j < k:
            m.cons.add(m.start[j] + JOBS[j]['duration'] <= m.start[k] + BigM*(1-m.y[j,k]))
            m.cons.add(m.start[k] + JOBS[k]['duration'] <= m.start[j] + BigM*(m.y[j,k]))

SolverFactory('glpk').solve(m)

for j in J:
    JOBS[j]['start'] = m.start[j]()
    JOBS[j]['finish'] = m.start[j]() + JOBS[j]['duration']
    JOBS[j]['pastdue'] = m.pastdue[j]()
    JOBS[j]['early'] = m.early[j]()
    JOBS[j]['ispastdue'] = m.ispastdue[j]()
    
# display table of results
df = pd.DataFrame(JOBS)
df['Total'] = df.sum(axis=1)
df.loc[['due','finish','release','start'],'Total'] = ''
display(df)
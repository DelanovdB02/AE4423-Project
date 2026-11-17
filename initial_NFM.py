
from gurobipy import *

# Data
Airports = ['A1', 'A2', 'A3']
airports = range(len(Airports))

CASK = 0.12
LF = 0.75
s = 120
sp = 870
LTO = 20/60
BT = 10 * 7
AC = 2
y = 0.18  # yield

q = [[0, 1000, 200],
     [1000, 0, 300],
     [200, 300, 0]]

distance = [[0, 2236, 3201],
            [2236, 0, 3500],
            [3201, 3500, 0]]

# Start modelling optimization problem
m = Model('practice')

x = {}
z = {}

for i in airports:
    for j in airports:
        x[i,j] = m.addVar(
            obj=y * distance[i][j],
            lb=0,
            vtype=GRB.INTEGER
        )

        z[i,j] = m.addVar(
            obj=-CASK * distance[i][j] * s,
            lb=0,
            vtype=GRB.INTEGER
        )

m.update()

m.setObjective(m.getObjective(), GRB.MAXIMIZE)  # Maximize profit

# C1: Demand constraint
for i in airports:
    for j in airports:
        m.addConstr(x[i,j] <= q[i][j])

# C2: Capacity constraint
for i in airports:
    for j in airports:
        m.addConstr(x[i,j] <= LF * s * z[i,j])

# C3: Flow balance
for i in airports:
    m.addConstr(
        quicksum(z[i,j] for j in airports) ==
        quicksum(z[j,i] for j in airports)
    )

# C4: Available aircraft time
m.addConstr(
    quicksum(
        (distance[i][j]/sp + LTO) * z[i,j]
        for i in airports
        for j in airports
    ) <= BT * AC
)

m.update()

# m.write('test.lp')

# Set time constraint for optimization (5 minutes)
# m.setParam('TimeLimit', 1 * 60)
# m.setParam('MIPGap', 0.009)

m.optimize()

# m.write("testout.sol")

status = m.status

if status == GRB.Status.UNBOUNDED:
    print('The model cannot be solved because it is unbounded')

elif status == GRB.Status.OPTIMAL:
    f_objective = m.objVal

    print('***** RESULTS ******')
    print('\nObjective Function Value: \t %g' % f_objective)

elif status == GRB.Status.INFEASIBLE:
    print('The model is infeasible')

else:
    print('Optimization was stopped with status %d' % status)


# Print out Solutions
if status == GRB.Status.OPTIMAL:

    print()
    print("Frequencies:----------------------------------")
    print()

    for i in airports:
        for j in airports:
            if z[i,j].X > 0:
                print(
                    Airports[i],
                    ' to ',
                    Airports[j],
                    z[i,j].X
                )

    print()
    print("Passengers:-----------------------------------")
    print()

    for i in airports:
        for j in airports:
            if x[i,j].X > 0:
                print(
                    Airports[i],
                    ' to ',
                    Airports[j],
                    x[i,j].X
                )

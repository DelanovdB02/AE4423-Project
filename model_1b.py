"""
Passenger Mix Flow using Keypath Formulation with Column Generation Algorithm

Structure:
1. Data loading
2. Parameters
3. Full mathematical programming
3. Model and programming validation
4. RMS + column generation
5. Results and comparison
"""
# 1. Data loading
from initialization_1b import (
    L, P, CAP, D, fare,
    delta, Q, origin, destination,
    P_alt, b
)

import pandas as pd
import gurobipy as gp
from gurobipy import GRB

# 2. Parameters
   # Created in initialization_1b

# 3. Mathematical model
model = gp.Model("Passenger_reallocation")

# Decision variables
    # t[p, r] = number of pax which are originally assigned (or desire) itinereary p 
    #            but are reassigned to alternative itinerary r. t[p, p] is not included as it would equal x[p,p] (relationship there)

t = model.addVars([(p,r) for p in P for r in P_alt[p]],
                  lb = 0,
                  vtype=GRB.CONTINUOUS, name = 't')

# Objective function
    # Minimize the lost revenue of reallocation
model.setObjective(gp.quicksum(
    (fare[p] - b[p,r]*fare[r]) * t[p, r]
    for p in P for r in P_alt[p]),
    GRB.MINIMIZE)

# Constraints
    # C1: Capacity Constraints on the number of pax removed from flight i and recaptured from flight i. This should be at least bigger than the excess demand.
        # If there is demand spillage in flight i, pax need to be spilled (Qi - CAPi > 0)
        # If there is capacity surplus in flight i, pax can be recaptured (Qi - CAPi < 0)

for i in L:
    model.addConstr(
        gp.quicksum(
            delta[i, p] * t[p, r]
            for p in P
            for r in P_alt[p]
        )
        -
        gp.quicksum(
            delta[i, p] * b[r, p] * t[r, p]
            for r in P
            for p in P_alt[r]
        )
        >= Q[i] - CAP[i],
        name=f"Capacity_{i}"
    )

    # C2: Number of pax must be lower than demand
for p in P:
    model.addConstr(
        gp.quicksum(t[p, r] for r in P_alt[p])
                     <= D[p],
                    name =f"Demand_{p}"
    )

    # C3: Number of pax is positive
for p in P:
    for r in P_alt[p]:
        t[p, r] >= 0


# Solve model
model.optimize()

# print("capacities per flight (load, capacity)")

# for i in L:
#     removed = sum(
#         delta[i, p] * t[p, r].X
#         for p in P for r in P_alt[p]
#     )

#     added = sum(
#         delta[i, r] * b[p, r] * t[p, r].X
#         for p in P for r in P_alt[p]
#     )

#     final_load = Q[i] - removed + added

#     print(
#         f"Flight {i}: "
#         f"Load = {final_load:.2f}, "
#         f"Capacity = {CAP[i]}, "
#         f"Remaining = {CAP[i] - final_load:.2f}"
#     )

if model.Status == GRB.OPTIMAL:

    print("\n--- OPTIMAL SOLUTION ---")

    # Minimum revenue loss
    print(f"Minimum revenue loss: €{model.ObjVal:,.2f}")

    # Total unconstrained demand
    total_demand = sum(D[p] for p in P)
    print(f"Total passenger demand: {total_demand:,.2f}")

    # Total passengers spilled
    total_spilled = sum(t[p, -1].X for p in P)
    print(f"Total passengers spilled: {total_spilled:,.2f}")

    # Total passengers successfully recaptured
    total_recaptured = sum(
        b[p, r] * t[p, r].X
        for p in P
        for r in P_alt[p]
        if r != -1
    )
    print(f"Total passengers recaptured: {total_recaptured:,.2f}")

    # # Recapture rates for alternative itineraries
    # print("\n--- RECAPTURE RATES ---")

    # for p in P:
    #     for r in P_alt[p]:
    #         print(f"Itinerary {p} -> {r}: {b[p, r]:.2%}")

else:
    print("No optimal solution found.")
    print(f"Solver status: {model.Status}")


# Simple system KPIs to check
total_demand = sum(D[p] for p in P)
potential_revenue = sum(D[p] * fare[p] for p in P)
total_capacity = sum(CAP[i] for i in L)
total_spilled = sum(t[p, -1].X for p in P)
total_recaptured = sum(b[p, r] * t[p,r].X for p in P for r in P_alt[p] if r != -1) # X returns optimal number, gurobi

print(f"Total unconstrained demand {total_demand}")
print(f"Total flight capacity {total_capacity}")
print(f"Potential revenue {potential_revenue} [EUR]")
print(f"Total spilled pax: {total_spilled}")
print(f"Total recaptured pax: {total_recaptured}")

total_reassigned = sum(
    t[p, r].X
    for p in P
    for r in P_alt[p]
    if r != -1
)

total_accepted = sum(
    b[p, r] * t[p, r].X
    for p in P
    for r in P_alt[p]
    if r != -1
)

print(f"Total passengers reassigned: {total_reassigned:.2f}")
print(f"Total passengers accepting alternatives: {total_accepted:.2f}")

# Init shows demand is almost twice flight capacity sum -> capacity pressure.

# Total passengers who do not travel
total_rejected = total_reassigned - total_recaptured

total_lost = total_spilled + total_rejected

total_travelled = total_demand - total_lost

print(f"Passengers rejecting alternatives: {total_rejected:.2f}")
print(f"Total passengers not travelling: {total_lost:.2f}")
print(f"Total passengers travelling: {total_travelled:.2f}")

print(f"Share of demand travelling: {total_travelled / total_demand:.2%}")
print(f"Share of demand lost: {total_lost / total_demand:.2%}")

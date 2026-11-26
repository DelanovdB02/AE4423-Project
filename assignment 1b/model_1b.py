"""
Passenger Mix Flow full Leg-Based Model Formulation

Structure:
1. Data loading
2. Parameters
3. Full mathematical programming
4. Model output & results
5. Model validation
"""

# Import packages
import pandas as pd
import gurobipy as gp
from gurobipy import GRB

# --------------- #
# 1. Data loading
# --------------- #
from initialization_1b import (
    L, P, CAP, D, fare,
    delta, Q, origin, destination,
    P_alt, b
)

from kpis_1b import compute_kpis, kpis
from validation import validate_pax, validate_cap, sensitivity_analysis

# ------------- #
# 2. Parameters
# ------------- #
   # Created in initialization_1b


# --------------------- #
# 3. Mathematical model
# --------------------- #
def math_model(verbose=True):
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
    model.Params.OutputFlag = int(verbose)
    model.optimize()

# ------------------------- #
# 4. Model output & results
# ------------------------- #
    if model.Status == GRB.OPTIMAL and verbose:
        KPI = compute_kpis(model, t)
        kpis(KPI)

        # Flag if False result based on certain conditions
        validate_pax(KPI)
        validate_cap(KPI, L)

    return model, t

math_model()

# ------------------- #
# 5. Model validation
# ------------------- #

run_sensitivity = False
if run_sensitivity:
    sensitivity_results = sensitivity_analysis(math_model)

# Time-based demand integration 
#   -> advice to focus on certain flight or aircraft types in an itereative/future process
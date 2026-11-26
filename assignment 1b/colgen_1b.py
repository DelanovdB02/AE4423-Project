"""
Passenger Mix Flow using Keypath Formulation with Column Generation Algorithm

Structure:
1. Data loading
2. Parameters
3. Restricted Master Problem & Column Generation
4. Model Output & Results
5. Model Validation


Start with only spilled columns: 
- t[p, -1] being the RMP
Start adding columns which reduce the negative cost
"""

# import packages
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
max_iter = 10
tol = 1e-6

# ------------------------------------------------ #
# 3. Restricted Master Problem & Column Generation
# ------------------------------------------------ #
def column_generation():

    # RMP: initially only include the spill columns
    master = gp.Model("Passenger_reallocation_cg")

    # Decision variables
        # t[p, r] = number of passengers originally assigned to itinerary p
        #           but reassigned to alternative itinerary r.
        # t[p, 0] = number of passengers spilled.
        # t[p, p] is excluded because these passengers remain on their original itinerary.

    t = {}
    
    # ---- Define constraints ---- # 
    # (decision variables not created, so empty constraints)
        # New variables get added later in gp.Column where each variable calculates its sole contribution to capacity constraints.
        # C1: Capacity constraints
    cap_con = {}
    for i in L:
        cap_con[i] = master.addConstr(gp.LinExpr() >= Q[i] - CAP[i],
                                      name=f"Capacity_{i}")

        # C2: Demand constraints
    dem_con = {}
    for p in P:
        dem_con[p] = master.addConstr(gp.LinExpr() <= D[p], 
                                      name = f"Demand_{p}")

    # ---- Add decision vairables (New columns) ---- #
    def add_column(p, r):
        cost = fare[p] - b[p, r] * fare[r]

        coeffs = []
        constrs = []

        # Only change capacity constraints as these depend on how many seats a pax occupies on flight i
        # Demand coefficient is always 1 because each pax can be reallocated once
        for i in L:
            capacity_coeff = (delta[i, p] - delta[i, r] * b[p, r])

            coeffs.append(capacity_coeff)
            constrs.append(cap_con[i])

        # Demand constraint coefficient
        coeffs.append(1)
        constrs.append(dem_con[p])

        # Add variable to RMP
        t[p, r] = master.addVar(lb=0, obj=cost, vtype=GRB.CONTINUOUS,
            name=f"t[{p},{r}]", column=gp.Column(coeffs, constrs))


    # Add initial columns (fictitious itinerary r = 0 being the buffer pax)
    for p in P:
        add_column(p, -1)

    master.update()

    # --- Column generation --- #
    
    # Get duals and solve using price problem
        # Iterate
    # Determine if enough columns (convergence)

    exit_condition = False
    iteration = 0

    while True:
        # Solve RMP
        master.optimize()

        if master.Status != GRB.OPTIMAL:
            print("RMP did not find optimal")
            break

        # Get duals (constraint values) being the marginal value
        pi_capacity = {}
        for i in L:
            pi_capacity[i] = cap_con[i].Pi

        pi_demand = {}
        for p in P:
            pi_demand[p] = dem_con[p].Pi


        # Solving pricing problem with the duals to calculate reduced cost of new column
        # Create list of new columns to store
        new_columns = []

        for p in P:
            best_cost = float("inf")         # Lowest reduced cost for itin p
            best_r = None               # Lowest reduced cost for alternative itin r

            for r in P_alt[p]:
                if r == p or r == 0:    # If pax stay on itin or spilled
                    continue
                if (p,r) in t:          # If column exists already
                    continue

                # Dual version of add_column part
                cost = fare[p] - b[p, r] * fare[r]
                capacity_dual = sum(pi_capacity[i] * (delta[i, p]
                                        - delta[i, r] * b[p, r])
                                    for i in L)
                reduced_cost = (cost - capacity_dual - pi_demand[p])

                # Find alternative with lowest reduction
                if reduced_cost < best_cost:
                    best_cost = reduced_cost
                    best_r = r

            if best_r is not None and best_cost < -tol:
                new_columns.append((p, best_r, best_cost))

    
        # Check for convergence
        if iteration >= max_iter:
            print("Maximum # of iterations")
            break

        if not new_columns:
            converged = True
            print(f"Column generation converged after {iteration} iterations")
            break

        # Add new columns:
        for p, r, rc in new_columns:
            add_column(p, r)
            print(f"Iteration {iteration + 1}: "
                  f"Added column t[{p},{r}],"
                  f"reduced cost = {rc:.1f}")

        master.update()

        iteration += 1

    # ------------------------- #
    # 4. Model output & results
    # ------------------------- #

    if master.Status == GRB.OPTIMAL:
        print("\nFinal RMP solution")
        print(f"Objective value: {master.ObjVal:.6f}")

        # KPI = compute_kpis(master, t)
        # kpis(KPI)

        # # Model validation
        # validate_pax(KPI)
        # validate_cap(KPI, L)

    return master, t

column_generation()

# ------------------- #
# 5. Model validation
# ------------------- #

run_sensitivity = False
if run_sensitivity:
    sensitivity_results = sensitivity_analysis(column_generation)
"""
KPIs are shared by model_1b.py and colgen_1b.py
Input of KPI equals the value of t[p,r]
"""

from initialization_1b import (
    L, P, CAP, D, fare,
    delta, Q, origin, destination,
    P_alt, b
)

def compute_kpis(model, t):
    KPI = {}

    # Passengers
    KPI['total_demand'] = sum(D[p] for p in P)
    KPI['spilled'] = sum(t[p, -1].X for p in P)
    KPI['reassigned'] = sum(t[p, r].X
    for p in P for r in P_alt[p]
    if r != -1
    )
    KPI['recaptured'] = sum(b[p, r] * t[p, r].X
    for p in P for r in P_alt[p]
    if r != -1
    )
    KPI['rejected'] = KPI['reassigned'] - KPI['recaptured']
    KPI['lost'] = KPI['spilled'] + KPI['rejected']
    KPI['travelling'] = KPI['total_demand'] - KPI['lost']

    KPI['spill_rate'] = KPI['spilled'] / KPI['total_demand']
    KPI['recapture_rate'] = KPI['recaptured'] / KPI['reassigned'] if KPI['reassigned'] > 0 else 0
    KPI['lost_share'] = KPI['lost'] / KPI['total_demand']


    # Load and capacities per flight (Qi - removed + recaptured)
    load = {}
    for i in L:
        removed = sum(
            delta[i, p] * t[p, r].X
            for p in P for r in P_alt[p]
        )

        added = sum(
            delta[i, r] * b[p, r] * t[p, r].X
            for p in P for r in P_alt[p]
        )

        load[i] = Q[i] - removed + added
    KPI['load'] = load


    # Capacities
    KPI['total_capacity'] = sum(CAP[i] for i in L)
    KPI['total_leg_demand'] = sum(Q[i] for i in L)
    KPI['seats_used'] = sum(load.values())
    KPI['unused_seats'] = KPI['total_capacity'] - KPI['seats_used']
    KPI['load_factor'] = KPI['seats_used'] / KPI['total_capacity']
    KPI['flights_full'] = sum(1 for i in L if load[i] >= CAP[i])


    # Revenues
    KPI['potential_revenue'] = sum(D[p] * fare[p] for p in P)
    KPI['lost_revenue'] = model.ObjVal
    KPI['retained_revenue'] = KPI['potential_revenue'] - KPI['lost_revenue']
    KPI['revenue_recovered'] = sum(b[p, r] * fare[r] * t[p, r].X
    for p in P for r in P_alt[p] if r != -1
    )

    return KPI

####################################################################################
###### DUAL VARIABLES (only for column generation algo) ####
# Indicate the final objective value, the total number of passengers spilled, the optimal
# decision variables associated with the first 5 passengers itineraries and the optimal dual
# variables for the first 5 flights of the schedule. Provide also information regarding the
# number of columns in the RMP before and after running the column generation algorithm,
# and the number of iterations required to converge.
###############################################################################

# Automated above KPIs to be printed with code using chatgpt command:
def kpis(KPI):
    print("\n--- Passengers ---")
    print(f"Total demand:       {KPI['total_demand']:,.0f} passengers")
    print(f"Spilled:            {KPI['spilled']:,.0f} passengers")
    print(f"Reassigned:         {KPI['reassigned']:,.0f} passengers")
    print(f"Recaptured:         {KPI['recaptured']:,.0f} passengers")
    print(f"Rejected:           {KPI['rejected']:,.0f} passengers")
    print(f"Lost:               {KPI['lost']:,.0f} passengers")
    print(f"Travelling:         {KPI['travelling']:,.0f} passengers")
    print(f"Spill rate:         {KPI['spill_rate']:.1%}")
    print(f"Recapture rate:     {KPI['recapture_rate']:.1%}")
    print(f"Lost share:         {KPI['lost_share']:.1%}")

    print("\n--- Capacities ---")
    print(f"Total capacity:     {KPI['total_capacity']:,.0f} seats")
    print(f"Total leg demand:   {KPI['total_leg_demand']:,.0f} passengers")
    print(f"Seats used:         {KPI['seats_used']:,.0f} seats")
    print(f"Unused seats:       {KPI['unused_seats']:,.0f} seats")
    print(f"Load factor:        {KPI['load_factor']:.1%}")
    print(f"Flights full:       {KPI['flights_full']}/{len(L)} ({KPI['flights_full']/len(L):.1%})")

    print("\n--- Revenues ---")
    print(f"Potential revenue:  €{KPI['potential_revenue']:,.2f}")
    print(f"Lost revenue:       €{KPI['lost_revenue']:,.2f} (MINIMIZED)")
    print(f"Retained revenue:   €{KPI['retained_revenue']:,.2f}")
    print(f"Revenue recovered by recapturing:  €{KPI['revenue_recovered']:,.2f}")
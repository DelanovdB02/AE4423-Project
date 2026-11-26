
from initialization_1b import L, P, D, CAP, b, Q, delta
from kpis_1b import compute_kpis


def validate_pax(KPI):
    if KPI['total_demand'] != KPI['travelling'] + KPI['lost']:
        print("Total demand invalid")
    if KPI['lost'] != KPI['spilled'] + KPI['rejected']:
        print("Total lost invalid")


def validate_cap(KPI, L):
    if KPI['flights_full'] >= len(L):
        print("Total flight capacity violated")
    if KPI['total_capacity'] != KPI['seats_used'] / KPI['load_factor']:
        print("Total LF capacity violated")
    if KPI['total_capacity'] != KPI['seats_used'] + KPI['unused_seats']:
        print("Total seat capacity violated")


# Used ChatGPT for sensitivity initialization with code prompt on the three scenarios.

def sensitivity_analysis(math_model):

    # Save original parameters
    D_original = D.copy()
    CAP_original = CAP.copy()
    b_original = b.copy()
    Q_original = Q.copy()

    scenarios = {
        "Demand +10%": "demand",
        "Capacity +10%": "capacity",
        "No recapture": "recapture"
    }

    results = {}

    try:
        for name, scenario in scenarios.items():

            print(f"\n{'=' * 50}")
            print(f" SENSITIVITY SCENARIO: {name}")
            print(f"{'=' * 50}")

            # Restore original parameters
            D.update(D_original)
            CAP.update(CAP_original)
            b.update(b_original)
            Q.update(Q_original)

            # Modify parameters
            if scenario == "demand":
                for p in P:
                    D[p] *= 1.10

                for i in L:
                    Q[i] = sum(
                        delta[i, p] * D[p]
                        for p in P
                    )

            elif scenario == "capacity":
                for i in L:
                    CAP[i] *= 1.10

            elif scenario == "recapture":
                for key in b:
                    b[key] = 0

            # Run model without printing model output
            model, t = math_model(verbose=False)

            if model.Status == 2:
                KPI = compute_kpis(model, t)
                results[name] = KPI

                print("\nKPI RESULTS")
                print("-" * 30)
                print(f"Lost share:    {KPI['lost_share']:.1%}")
                print(f"Lost revenue:   €{KPI['lost_revenue']:,.2f}")
                print(f"Recapture rate: {KPI['recapture_rate']:.1%}")
                print(f"Load factor:    {KPI['load_factor']:.1%}")

            else:
                print(f"Model did not find an optimal solution. Status: {model.Status}")

            model.dispose()

    finally:
        # Restore original parameters
        D.update(D_original)
        CAP.update(CAP_original)
        b.update(b_original)
        Q.update(Q_original)

    return results
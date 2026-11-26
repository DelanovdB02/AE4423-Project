"""
Passenger Mix Flow using Keypath Formulation with Column Generation Algorithm

Structure:
1. Data loading
2. Parameters
3. Restricted Master Problem & Column Generation
5. Model Output & Results
6. Model Validation


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

# ------------------------------------------------ #
# 3. Restricted Master Problem & Column Generation
# ------------------------------------------------ #
def column_generation():

    # 1. RMP: initially only include the spill columns
    master = gp.Model("Passenger_reallocation_cg")



    # Get duals and solve using price problem
    # Determine if enough columns (convergence)


    # Iterate
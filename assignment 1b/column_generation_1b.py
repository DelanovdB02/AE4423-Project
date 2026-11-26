"""
Passenger Mix Flow using Keypath Formulation with Column Generation Algorithm

Structure:
1. Data loading
2. Parameters
3. Full mathematical programming
3. Model and programming validation
4. RMS + column generation
5. Results and comparison


Start with only spilled columns: 
- t[p, -1] being the RMP
Start adding columns which reduce the negative cost
"""


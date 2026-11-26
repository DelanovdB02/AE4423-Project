""""
Passenger Mix Flow

The airline has a daily flight schedule (as created in 1a, data retreived) for which we want to study the best passenger mix flow to maximize revenue.

-------------------

The goal of the second assignment is to identify the best mix of passengers from each itinerary to carry on each flight leg.
The problem is optimized for a single days of operations and considers spill costs and recapture opportunities.
Capacity constraints per flight leg and limited unconstrained demand per itinerary needs to be verified.

------------------ 

The following data is used:
- 1b_Group_4.xlsx
   with an airline daily flight schedule, passenger itineraries and flight pairs

-------------------

The following assumptions are made:
- 10% of the pax will refuse rescheduling
- extra 10% will refuse reschedule IF t_dep moves 1-3 hours
- extra 20% will refuse reschedule IF t_dep moves < 3 hours
- extra 30% will refuse reschedule IF t_flight increases by > 2 hours

-------------------

The following steps are taken:
- 1. Generate recapture possibilites
- 2. Define mathematical model (leg-based)
- 3. Calculate revenues and spill costs
- 4. Implement the RMP
- 5. Implement column generation using reduce costs
- 6. Solve, validate & calculate KPI's
- 7. Evaluate & report
"""

import pandas as pd
import matplotlib.pyplot as plt

# ---- 1. Data initialization ----- #

flights = pd.read_excel('data/1b_Group_4.xlsx', sheet_name = 0)
itin = pd.read_excel('data/1b_Group_4.xlsx', sheet_name = 1)

flights = flights.rename(columns={
    "Flight No.": "flight_id",
    "Capacity": "capacity",
    "Departure": "departure_time",
    "Arrival": "arrival_time",
    "Destination": "destination",
    "Origin": "origin"
})

itin = itin.rename(columns={"Itinerary": "itinerary_id",
    "Demand": "demand",
    "Price [EUR]": "fare",
    "Flight 1":"leg1",
    "Flight 2":"leg2",    
    "Destination": "destination",
    "Origin":"origin"})

# ---- 2. Data preparation ----- #

# -- Creating sets --
L = flights["flight_id"].astype(str).str.strip().tolist()
P = itin["itinerary_id"].astype(int).tolist()

# -- Creating parameters --
# Capacity per flight
CAP = dict(zip(L, flights["capacity"]))

# Demand per itinerary
D = dict(zip(P, itin["demand"]))

# Fare per itinerary
fare = dict(zip(P, itin["fare"]))

   # Fictitious itinerary of 0
fare[-1] = 0 # fictitious itin has zero fare as no ticket revenue generated (spilled)


# Origin and destination per itinerary
origin = dict(zip(P, itin["origin"]))
destination = dict(zip(P, itin["destination"]))

# Set of all pax itinieraries with recapture from p (r index)
P_alt = {}
for p in P:
    # Find all itineraries r that
    P_alt[p] = [r for r in P
                if r != p and                      # Are not original itin p
                origin[r] == origin[p] and         # Have same origin as initial itin p
                destination[r] == destination[p]]  # Have same destination as initial itin p 
    P_alt[p].append(-1) # Fictitious itinierary 0 (spilled pax)

# Check duplicate itinerary IDs
print("Duplicate itinerary IDs:", itin["itinerary_id"].duplicated().sum())

# Check duplicate decision variable keys
keys = [(p, r) for p in P for r in P_alt[p]]

print("Total decision variable keys:", len(keys))
print("Unique decision variable keys:", len(set(keys)))

# ---- 3. Create itinerary legs ----- #

# delta[i, p] = 1 if flight i is part of itinerary p, 0 otherwise

delta = {}

for _, row in itin.iterrows():
    p = row["itinerary_id"]
    itin_flights = [row["leg1"], row['leg2']] # Collect flights belonging to itin
    itin_flights = [i for i in itin_flights if pd.notna(i)] # Remove empty legs

    for i in L:
        delta[i,p] = int(i in itin_flights)

# For fictitious
for i in L:
    delta[i, -1] = 0 # fictitious flight incidence is zero as no flight actually involved (spilled)


# ---- 4. Calculate Unconstrained flight demand ----- #

# Q[i] = total demand wanting to use flight i (sum of D[p] times delta[i,p])
Q = {}

for i in L:
    Q[i] = sum(delta[i,p] * D[p] for p in P)


# ---- 5. Calculate recapture rates ---- #
# First caulculate dep times and durations

# Convert flight times to minutes after midnight
flights["departure_time"] = pd.to_datetime(flights["departure_time"])
flights["arrival_time"] = pd.to_datetime(flights["arrival_time"])

flight_dep = dict(zip(L, flights["departure_time"].dt.hour * 60 +
                         flights["departure_time"].dt.minute))

flight_arr = dict(zip(L, flights["arrival_time"].dt.hour * 60 +
                         flights["arrival_time"].dt.minute))

# Calculate departure time and duration per itinerary
itin_dep = {}
itin_duration = {}

for _, row in itin.iterrows():

    p = row["itinerary_id"]
    first = row["leg1"]
    last = row["leg2"] if pd.notna(row["leg2"]) else first

    itin_dep[p] = flight_dep[first]

    arrival = flight_arr[last]
    if arrival < itin_dep[p]:
        arrival += 1440

    itin_duration[p] = arrival - itin_dep[p]

# Recapture rate
b = {}

for p in P:
   for r in P_alt[p]:
      if r == -1:
            b[p,r] = 1
            continue

      # Base refusal rate
      refusal_rate = 0.1

      # Refusal due to departure time differences
      dep_diff = abs(itin_dep[r] - itin_dep[p]) / 60
      
      if  1 <= dep_diff <= 3:
            refusal_rate += 0.1
      elif dep_diff > 3:
            refusal_rate += 0.2
        
      # Refusal if journey time more than 2 hours longer
      duration_diff = (itin_duration[r] - itin_duration[p]) / 60

      if duration_diff > 2:
          refusal_rate += 0.3

      b[p, r] = 1 - refusal_rate

# # ---- Check code (with chat) ----- #
# print("\n--- FLIGHT CAPACITY AND DEMAND ---")

# for i in L:
#     print(
#         f"Flight {i}: "
#         f"Capacity = {CAP[i]}, "
#         f"Demand = {Q[i]}, "
#         f"Excess demand = {Q[i] - CAP[i]}"
#     )


# print("\n--- FLIGHT-ITINERARY INCIDENCE MATRIX ---")

# delta_table = pd.DataFrame(
#     [[delta[i, p] for p in P] for i in L],
#     index=L,
#     columns=P
# )

# print(delta_table)

# # Number of flights per itinerary
# print(delta_table.sum(axis=0).value_counts()) # Check if itinerary has one flight, and if it is consistent with incidence matrix & itinerary data





# ------------------------------------------------------------------ #
# ----- Initial plot on schedule ------- #

# flights['Arrival_dt'] = pd.to_datetime(flights['Arrival'], format='mixed')
# flights['Departure_dt'] = pd.to_datetime(flights['Departure'], format='mixed')

# flights['Arrival_hour'] = flights['Arrival_dt'].dt.hour + flights['Arrival_dt'].dt.minute / 60
# flights['Departure_hour'] = flights['Departure_dt'].dt.hour + flights['Departure_dt'].dt.minute / 60

# flights = flights.sort_values('Departure_hour').reset_index(drop=True)

# fig, ax = plt.subplots(figsize=(16, 8))

# for i, row in flights.iterrows():
#     ax.barh(
#         y=i,
#         width=row['Departure_hour'] - row['Arrival_hour'],
#         left=row['Arrival_hour'],
#         height=2
#     )
# start = int(max(0,flights['Departure_hour'].min()-1))

# ax.set_xlim(start, 24)
# ax.set_xticks(range(start,25))
# ax.set_xticklabels(f'{h:02d}:00' for h in range(start, 25))
# ax.set_xlabel('Time of day')
# ax.set_title('Flight Schedule per Day')
# ax.yaxis.set_visible(False)
# plt.tight_layout()
# plt.show()

# -------------------------------------------------------------------- #


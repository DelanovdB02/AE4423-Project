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

flights = pd.read_excel('data/1b_Group_4.xlsx', sheet_name = 0)
itin = pd.read_excel('data/1b_Group_4.xlsx', sheet_name = 1)

flights['Arrival_dt'] = pd.to_datetime(flights['Arrival'], format='mixed')
flights['Departure_dt'] = pd.to_datetime(flights['Departure'], format='mixed')

flights['Arrival_hour'] = flights['Arrival_dt'].dt.hour + flights['Arrival_dt'].dt.minute / 60
flights['Departure_hour'] = flights['Departure_dt'].dt.hour + flights['Departure_dt'].dt.minute / 60

flights = flights.sort_values('Departure_hour').reset_index(drop=True)

fig, ax = plt.subplots(figsize=(16, 8))

for i, row in flights.iterrows():
    ax.barh(
        y=i,
        width=row['Departure_hour'] - row['Arrival_hour'],
        left=row['Arrival_hour'],
        height=2
    )
start = int(max(0,flights['Departure_hour'].min()-1))

ax.set_xlim(start, 24)
ax.set_xticks(range(start,25))
ax.set_xticklabels(f'{h:02d}:00' for h in range(start, 25))
ax.set_xlabel('Time of day')
ax.set_title('Flight Schedule per Day')
ax.yaxis.set_visible(False)
plt.tight_layout()
plt.show()
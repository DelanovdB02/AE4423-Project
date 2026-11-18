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
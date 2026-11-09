# EDA scripts

Run from the project root, after `python pipeline.py` has created
`output/cleaned_ride_bookings.csv`.

| Member | Script | Topic |
|---|---|---|
| 1 | `eda_member1_overview_quality.py` | data quality, distributions, outliers, correlations |
| 2 | `eda_member2_time_demand.py` | months, weekdays, hours, time of day |
| 3 | `eda_member3_vehicle_pricing.py` | vehicle types, fares, revenue, payments, ratings |
| 4 | `eda_member4_cancellations_locations.py` | cancellations, arrival times, locations, customers |

Each script saves charts in `eda_outputs/figures/`, a facts file
`eda_outputs/memberN_findings.md`, and a template
`eda_outputs/memberN_interpretation.md` that the member fills in.
`run_all_eda.py` (lead only) runs all four and writes `docs/EDA_report.md`.

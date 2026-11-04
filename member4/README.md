# NCR Ride Bookings ETL Pipeline

## Objective
Turn the raw Delhi-NCR ride-bookings CSV (150,000 rows x 21 columns) into a clean,
analysis-ready dataset plus a set of business reports that future Data Science projects
(demand forecasting, cancellation analysis, pricing) can use directly.

## Data Source
`ncr_ride_bookings.csv`, a public Kaggle dataset ("Uber Ride Analytics Dashboard"): structured CSV,
one static snapshot covering 2024. Answers to the six dataset questions are in
[`docs/dataset_description.md`](docs/dataset_description.md).

## ETL Workflow
![ETL flow](docs/etl_flow_diagram.png)

```
Data Source -> Extract -> Validate -> Clean -> Transform -> Generate Reports -> Load
```

| Function | Where | What it does |
|---|---|---|
| `extract()` | `etl/member1_extract_structural.py` | Reads the CSV (path or URL), prints records and columns, saves a raw copy in `raw_data/` |
| `transform()` | `pipeline.py` | Runs the 12 ordered transformations, then builds 14 reports |
| `load()` | `etl/member4_reports_and_load.py` | Writes the cleaned data to `output/` and every report to `reports/` |
| `run_etl_pipeline()` | `pipeline.py` | Extract -> Transform -> Load; runs only when the file is executed directly |

## Team and Work Split
| Member | Module | Responsibility |
|---|---|---|
| 1 | `etl/member1_extract_structural.py` | `extract()`; rename, text standardising, duplicates, dates; dataset description and flow diagram |
| 2 | `etl/member2_missing_and_validation.py` | Merge reason columns, missing values, validation |
| 3 | `etl/member3_types_and_features.py` | Data types, calculated columns, categories, outliers, sorting |
| 4 | `etl/member4_reports_and_load.py` | 14 reports, `load()`, README, final run and screenshots |

## Project Structure
```
NCR_Ride_Bookings_ETL/
├── raw_data/        original CSV (+ auto-generated raw copy, git-ignored)
├── reports/         14 report CSVs
├── screenshots/     terminal screenshots of the runs
├── output/          cleaned_ride_bookings.csv
├── etl/             one module per member + shared common.py
├── tests/           pytest checks, one file per member
├── docs/            dataset description, flow diagram
├── pipeline.py
├── check_member.py  checkpoint script used while merging
├── README.md
└── requirements.txt
```

## How to Run
```powershell
pip install -r requirements.txt
python pipeline.py                      # uses raw_data/ncr_ride_bookings.csv
python pipeline.py --source <csv path or URL>
pip install -r requirements-dev.txt     # optional: tests + lint
pytest ; flake8 .
```

## Transformations (12) and why
| # | By | Transformation | Why it was necessary |
|---|---|---|---|
| 1 | M1 | Rename columns to snake_case with units (`Avg VTAT` -> `avg_vtat_min`) | Spaces and abbreviations are error-prone in code |
| 2 | M1 | Standardise text: strip the literal `"` around IDs, trim spaces, Title Case locations | IDs were stored as `"CNR123"`, which breaks joins and lookups |
| 3 | M1 | Remove duplicates (exact rows, then repeated `booking_id`): **1,233 rows** | A primary key must be unique or rides are double-counted |
| 4 | M1 | Convert `date` + `time` into one datetime; derive month, weekday, hour, weekend flag | Text dates cannot be grouped or plotted over time |
| 5 | M2 | Merge 3 reason columns into `cancelled_by` + `reason`; drop 3 flag columns that only ever hold `1` | 6 sparse columns became 2 usable ones, nothing lost |
| 6 | M2 | Validate and filter: ratings 1-5, fare/distance/times > 0, pickup != drop, valid timestamp | Removes impossible values. This dataset passed with **0 rows removed**, and the check guards future loads |
| 7 | M2 | Handle missing values: label categoricals `Not Applicable`, fill numeric nulls with 0. **The cleaned file has 0 nulls** | Cancelled rides never have a fare, distance or rating, so 0 means "did not happen" (valid ratings are 1-5, so 0 = not rated). Validation runs first so the 0s are not rejected, and reports ignore the 0s so averages stay correct |
| 8 | M3 | Change data types (category, int16, bool, datetime) | Correct semantics and lower memory |
| 9 | M3 | Calculated columns: `fare_per_km`, `ride_outcome`, `is_completed`, `time_of_day` | Features analysts need immediately |
| 10 | M3 | Categories: `distance_category`, `fare_category` | Group continuous values in reports |
| 11 | M3 | Flag fare outliers with the IQR rule (`is_fare_outlier`, 3,410 rows) | Flagged, not deleted: high fares are rare but real |
| 12 | M3 | Sort chronologically | Deterministic output and time-series ready |

Each run also writes `reports/transformation_log.csv` with rows before/after for every step.

## Reports Generated (`reports/`)
`booking_status_summary` · `vehicle_type_report` · `monthly_report` · `hourly_demand_report` ·
`day_and_time_of_day_report` · `top10_pickup_locations` · `bottom10_pickup_locations` ·
`top10_routes` · `top10_highest_booking_values` · `bottom10_lowest_booking_values` ·
`payment_method_report` · `cancellation_reasons_report` · `summary_statistics` · `transformation_log`
(all `.csv`), plus the full cleaned dataset in `output/cleaned_ride_bookings.csv`.

Headline numbers: 148,767 unique bookings; 62.0% completed, 18.0% cancelled by drivers,
7.0% cancelled by customers, 7.0% no driver found, 6.0% incomplete; UPI is the most used payment
method (45% of completed rides).

## Challenges Faced
- IDs wrapped in literal quotes (`"CNR123"`) hid the real duplicates.
- About 1/3 of the numeric cells are null, but almost all of it is *structural* (a cancelled ride has no
  fare or rating). Inventing averages would be wrong, so they are filled with 0 ("did not happen") and the
  reports mask those 0s; the `is_completed` / `ride_outcome` columns tell analysts which rows are real rides.
- 1,233 `booking_id` values repeat across **different** rides (different date and places), so they are
  key collisions, not copies. Keeping the first occurrence enforces a unique key but discards about 0.8%
  of real rides, and this choice is documented.
- The data is very evenly distributed (every vehicle type averages about Rs 508 and 24.6 km), which
  suggests it is partly synthetic, so reports show few strong differences.
- Splitting one pipeline across four people: each module depends on the previous one, so we merged in
  order and used `check_member.py` as a checkpoint after every merge.

## Learning Outcomes
Structuring an ETL project; separating extract/transform/load; reading nulls by cause; keeping a
transformation log; writing small tests for data code; collaborating with Git branches, pull
requests and CI.

## Future Improvements
- Load into a database (SQLite/PostgreSQL) in addition to CSV; write Parquet for speed.
- Add charts and a Streamlit/Power BI dashboard on top of `reports/`.
- Schedule with Airflow or cron and add data-quality alerts.
- Fetch the dataset directly from the Kaggle API.
- Add location coordinates to enable geographic analysis.

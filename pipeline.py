"""ETL pipeline for the NCR (Delhi-NCR) ride bookings dataset.

Run directly:   python pipeline.py
Custom source:  python pipeline.py --source path/or/url/to/file.csv

Flow: extract() -> transform() -> load(), orchestrated by run_etl_pipeline().
The work is split across four member modules in etl/ (see TEAM_GUIDE.md).
"""
import argparse
import time

from etl.common import DEFAULT_SOURCE, BASE_DIR, StepLog, banner
from etl.member1_extract_structural import (convert_dates, extract, remove_duplicates,
                                            rename_columns, standardise_text)
from etl.member2_missing_and_validation import (handle_missing, merge_reason_columns,
                                                validate_and_filter)
from etl.member3_types_and_features import (add_calculated_columns, add_categories, change_dtypes,
                                            flag_outliers, sort_records)
from etl.member4_reports_and_load import generate_reports, load

__all__ = ["extract", "transform", "load", "run_etl_pipeline", "TRANSFORM_STEPS", "BASE_DIR"]

# (member, step name, why it is necessary, function). Order matters.
TRANSFORM_STEPS = [
    (1, "Rename columns (snake_case, units)", "consistent, code-friendly names", rename_columns),
    (1, "Standardise text (quotes/case)", "IDs wrapped in quotes; mixed text", standardise_text),
    (1, "Remove duplicate records", "duplicate booking_id double-counts rides", remove_duplicates),
    (1, "Convert dates + calendar fields", "text date/time cannot be grouped", convert_dates),
    (2, "Merge reason cols / drop flag cols", "6 sparse columns -> 2 usable ones", merge_reason_columns),
    (2, "Validate & remove invalid values", "ranges: rating 1-5, fare/distance > 0", validate_and_filter),
    (2, "Handle missing values (no nulls left)", "structural nulls -> label / 0", handle_missing),
    (3, "Change data types", "memory + correct semantics", change_dtypes),
    (3, "Create calculated columns", "fare_per_km, outcome, time_of_day", add_calculated_columns),
    (3, "Create categories (bins)", "distance and fare bands", add_categories),
    (3, "Flag fare outliers (IQR)", "keep but mark extreme fares", flag_outliers),
    (3, "Sort records chronologically", "deterministic, time-ordered output", sort_records),
]


def transform(df, upto_member=4):
    """Run the transformations (Members 1-3), then build the reports (Member 4).

    Returns (clean_df, reports_dict).
    """
    banner("STEP 2: TRANSFORM")
    log = StepLog()
    for member, name, why, func in TRANSFORM_STEPS:
        if member > upto_member:
            break
        before = len(df)
        df = func(df)
        log.add(member, name, why, before, len(df))
    reports = {}
    if upto_member >= 4:
        reports = generate_reports(df)
        reports["transformation_log.csv"] = log.to_frame()
    print(f"\nClean dataset: {df.shape[0]:,} rows x {df.shape[1]} columns")
    print(f"Reports built: {len(reports)}")
    return df, reports


def run_etl_pipeline(source=DEFAULT_SOURCE):
    """Extract -> Transform -> Load."""
    start = time.time()
    raw = extract(source)
    clean, reports = transform(raw)
    paths = load(clean, reports)
    banner("PIPELINE FINISHED")
    print(f"Raw {raw.shape[0]:,} x {raw.shape[1]}  ->  clean {clean.shape[0]:,} x {clean.shape[1]}")
    print(f"{len(paths)} files written in {time.time() - start:.1f}s")
    return clean, reports


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="NCR ride bookings ETL")
    parser.add_argument("--source", default=str(DEFAULT_SOURCE),
                        help="CSV path or URL (default: raw_data/ncr_ride_bookings.csv)")
    run_etl_pipeline(parser.parse_args().source)

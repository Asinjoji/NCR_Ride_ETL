"""Member 1: extract + structural cleaning."""
import shutil
from pathlib import Path

import pandas as pd

from etl.common import BASE_DIR, DEFAULT_SOURCE, RAW_COPY, RAW_DIR, banner


def extract(source=DEFAULT_SOURCE):
    """Read the raw CSV (local path or URL), report its size, save a raw copy."""
    banner("STEP 1: EXTRACT")
    source = str(source)
    print(f"Source           : {source}")
    df = pd.read_csv(source)
    print(f"Number of records: {len(df):,}")
    print(f"Number of columns: {df.shape[1]}")

    RAW_DIR.mkdir(exist_ok=True)
    if Path(source).exists():
        shutil.copyfile(source, RAW_COPY)
    else:  # remote source: write what we downloaded
        df.to_csv(RAW_COPY, index=False)
    print(f"Raw copy saved to: {RAW_COPY.relative_to(BASE_DIR)}")
    return df


def rename_columns(df):
    """T1. snake_case names are easier to code against than 'Avg VTAT'."""
    df = df.copy()
    df.columns = (df.columns.str.strip().str.lower()
                  .str.replace(r"[^a-z0-9]+", "_", regex=True).str.strip("_"))
    return df.rename(columns={"driver_ratings": "driver_rating",
                              "avg_vtat": "avg_vtat_min",
                              "avg_ctat": "avg_ctat_min",
                              "ride_distance": "ride_distance_km",
                              "booking_value": "booking_value_inr"})


def standardise_text(df):
    """T2. IDs arrive wrapped in literal quotes; locations/labels need uniform case."""
    df = df.copy()
    for col in ["booking_id", "customer_id"]:
        df[col] = df[col].astype(str).str.replace('"', "", regex=False).str.strip()
    for col in ["booking_status", "vehicle_type", "pickup_location", "drop_location",
                "payment_method", "reason_for_cancelling_by_customer",
                "driver_cancellation_reason", "incomplete_rides_reason"]:
        s = df[col].astype("object")
        df[col] = s.where(s.isna(), s.astype(str).str.strip().str.replace(r"\s+", " ", regex=True))
    for col in ["pickup_location", "drop_location"]:
        s = df[col].astype("object")
        df[col] = s.where(s.isna(), s.astype(str).str.title())
    return df


def remove_duplicates(df):
    """T3. booking_id is the primary key; repeated keys would double-count rides."""
    df = df.drop_duplicates()                       # exact duplicate rows
    return df.drop_duplicates(subset="booking_id", keep="first")


def convert_dates(df):
    """T4. Merge date + time into one timestamp and derive calendar features."""
    df = df.copy()
    df["booking_datetime"] = pd.to_datetime(df["date"].astype(str) + " " + df["time"].astype(str),
                                            errors="coerce")
    df = df.drop(columns=["date", "time"])
    dt = df["booking_datetime"].dt
    df["booking_date"] = dt.normalize()
    df["year"] = dt.year
    df["month"] = dt.month
    df["month_name"] = dt.month_name()
    df["day_of_week"] = dt.day_name()
    df["hour"] = dt.hour
    df["is_weekend"] = dt.dayofweek >= 5
    return df

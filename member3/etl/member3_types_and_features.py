"""Member 3: data types, features, categories, outliers, sorting."""
import numpy as np
import pandas as pd


def change_dtypes(df):
    """T8. Smaller, correct types: categories for labels, bool flags, int for counts."""
    df = df.copy()
    for col in ["booking_status", "vehicle_type", "payment_method", "cancelled_by",
                "reason", "day_of_week", "month_name"]:
        df[col] = df[col].astype("category")
    for col in ["year", "month", "hour"]:
        df[col] = df[col].astype("int16")
    df["booking_value_inr"] = df["booking_value_inr"].astype("float64")
    return df


def add_calculated_columns(df):
    """T9. Business features analysts will need straight away."""
    df = df.copy()
    status = df["booking_status"].astype(str)
    df["ride_outcome"] = np.select(
        [status == "Completed", status.isin(["Cancelled by Customer", "Cancelled by Driver"]),
         status == "Incomplete"],
        ["Successful", "Cancelled", "Incomplete"], default="No Driver Found")
    df["is_completed"] = status == "Completed"
    distance = df["ride_distance_km"].where(df["ride_distance_km"] > 0)
    df["fare_per_km"] = (df["booking_value_inr"] / distance).fillna(0).round(2)
    df["time_of_day"] = pd.cut(df["hour"], bins=[-1, 4, 11, 16, 20, 23],
                               labels=["Night", "Morning", "Afternoon", "Evening", "Late Night"]
                               ).astype(str).replace("Late Night", "Night")
    return df


def add_categories(df):
    """T10. Bin continuous fields so reports can group them."""
    df = df.copy()
    df["distance_category"] = pd.cut(df["ride_distance_km"], bins=[-1, 0, 10, 25, 40, np.inf],
                                     labels=["Not Applicable", "Short (<=10 km)", "Medium (10-25 km)",
                                             "Long (25-40 km)", "Very Long (>40 km)"])
    df["fare_category"] = pd.cut(df["booking_value_inr"], bins=[-1, 0, 250, 500, 1000, np.inf],
                                 labels=["Not Applicable", "Low (<=250)", "Medium (250-500)",
                                         "High (500-1000)", "Very High (>1000)"])
    return df


def flag_outliers(df):
    """T11. IQR rule on fare. Flagged (not deleted): big fares are real, rare trips."""
    df = df.copy()
    paid = df.loc[df["booking_value_inr"] > 0, "booking_value_inr"]   # ignore the 0 fillers
    q1, q3 = paid.quantile([0.25, 0.75])
    upper = q3 + 1.5 * (q3 - q1)
    df["is_fare_outlier"] = df["booking_value_inr"] > upper
    return df


def sort_records(df):
    """T12. Chronological order makes time-series work and diffs deterministic."""
    return df.sort_values(["booking_datetime", "booking_id"]).reset_index(drop=True)

"""Member 2: merge columns, missing values, validation."""
import numpy as np
import pandas as pd

from etl.common import NA_LABEL


def merge_reason_columns(df):
    """T5. Three sparse flag/reason pairs -> one 'cancelled_by' + one 'reason' column."""
    df = df.copy()
    cust = df["reason_for_cancelling_by_customer"]
    drv = df["driver_cancellation_reason"]
    inc = df["incomplete_rides_reason"]
    df["cancelled_by"] = np.select(
        [cust.notna(), drv.notna(), inc.notna()],
        ["Customer", "Driver", "Incomplete (in-ride)"], default=NA_LABEL)
    df["reason"] = cust.fillna(drv).fillna(inc).fillna(NA_LABEL)
    unwanted = ["cancelled_rides_by_customer", "cancelled_rides_by_driver", "incomplete_rides",
                "reason_for_cancelling_by_customer", "driver_cancellation_reason",
                "incomplete_rides_reason"]
    return df.drop(columns=unwanted)


def handle_missing(df):
    """T7. Remove every null. Nulls here are *structural*: a cancelled ride has no fare.

    Categorical nulls get an explicit label. Numeric nulls become 0 ("did not happen"):
    no fare, distance, wait time or rating exists for that booking. Valid ratings are 1-5,
    so 0 means "not rated". Reports ignore these zeros when averaging.
    """
    df = df.copy()
    df["payment_method"] = df["payment_method"].fillna(NA_LABEL)
    numeric_cols = ["booking_value_inr", "ride_distance_km", "avg_vtat_min", "avg_ctat_min",
                    "driver_rating", "customer_rating"]
    df[numeric_cols] = df[numeric_cols].fillna(0.0)
    return df


def validate_and_filter(df):
    """T6. Drop physically impossible values. Runs BEFORE nulls are filled with 0."""
    ok = pd.Series(True, index=df.index)
    ok &= df["booking_datetime"].notna()
    ok &= df["pickup_location"] != df["drop_location"]
    for col in ["booking_value_inr", "ride_distance_km", "avg_vtat_min", "avg_ctat_min"]:
        ok &= df[col].isna() | (df[col] > 0)
    for col in ["driver_rating", "customer_rating"]:
        ok &= df[col].isna() | df[col].between(1, 5)
    return df[ok]

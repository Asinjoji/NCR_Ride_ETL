import functools

import pandas as pd
import pytest

import pipeline

COLS = ["Date", "Time", "Booking ID", "Booking Status", "Customer ID", "Vehicle Type",
        "Pickup Location", "Drop Location", "Avg VTAT", "Avg CTAT",
        "Cancelled Rides by Customer", "Reason for cancelling by Customer",
        "Cancelled Rides by Driver", "Driver Cancellation Reason", "Incomplete Rides",
        "Incomplete Rides Reason", "Booking Value", "Ride Distance", "Driver Ratings",
        "Customer Rating", "Payment Method"]


def make_sample():
    n = None
    rows = [
        ["2024-01-02", "09:10:00", '"CNR1"', "Completed", '"CID1"', "Auto", " palam  vihar", "Jhilmil",
         5.0, 20.0, n, n, n, n, n, n, 300.0, 10.0, 4.5, 4.0, "UPI"],
        ["2024-01-02", "23:10:00", '"CNR1"', "Completed", '"CID2"', "Auto", "Palam Vihar", "Jhilmil",
         5.0, 20.0, n, n, n, n, n, n, 300.0, 10.0, 4.5, 4.0, "UPI"],
        ["2024-01-03", "10:00:00", '"CNR2"', "Cancelled by Driver", '"CID3"', "Bike", "AIIMS",
         "Inderlok", 4.0, n, n, n, 1.0, "Customer related issue", n, n, n, n, n, n, n],
        ["2024-01-04", "11:00:00", '"CNR3"', "Completed", '"CID4"', "Bike", "AIIMS", "Inderlok",
         4.0, 15.0, n, n, n, n, n, n, 400.0, 8.0, 9.0, 4.0, "Cash"],
        ["2024-01-05", "01:30:00", '"CNR4"', "Completed", '"CID5"', "Go Sedan", "Madipur", "Khandsa",
         6.0, 25.0, n, n, n, n, n, n, 5000.0, 30.0, 4.0, 5.0, "Credit Card"],
        ["2024-01-05", "02:30:00", '"CNR5"', "Completed", '"CID6"', "Auto", "Madipur", "Khandsa",
         6.0, 25.0, n, n, n, n, n, n, 450.0, 30.0, 4.0, 5.0, "UPI"],
    ]
    return pd.DataFrame(rows, columns=COLS)


@pytest.fixture
def sample():
    return make_sample()


def prepared(upto_member):
    """Sample data after the steps of members 1..upto_member (skips if one is a stub)."""
    df = make_sample()
    try:
        for member, _, _, func in pipeline.TRANSFORM_STEPS:
            if member > upto_member:
                break
            df = func(df)
    except NotImplementedError:
        pytest.skip("an earlier member's code is not merged yet")
    return df


def skip_if_stub(func, *args, **kwargs):
    try:
        return func(*args, **kwargs)
    except NotImplementedError:
        pytest.skip(f"{func.__name__} is not implemented yet")


def skips_stub(test):
    """Turn NotImplementedError (a member's code is still a stub) into a pytest skip."""
    @functools.wraps(test)
    def wrapper(*args, **kwargs):
        try:
            return test(*args, **kwargs)
        except NotImplementedError as exc:
            pytest.skip(f"not merged yet: {exc}")
    return wrapper

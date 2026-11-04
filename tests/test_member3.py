import pandas as pd

import etl.member3_types_and_features as m3
from tests.conftest import skips_stub, prepared, skip_if_stub


@skips_stub
def test_dtypes_changed():
    df = skip_if_stub(m3.change_dtypes, prepared(2))
    assert str(df["vehicle_type"].dtype) == "category"
    assert str(df["hour"].dtype) == "int16"


@skips_stub
def test_calculated_columns():
    df = m3.change_dtypes(prepared(2))
    out = skip_if_stub(m3.add_calculated_columns, df).set_index("booking_id")
    assert out.loc["CNR1", "fare_per_km"] == 30.0
    assert out.loc["CNR1", "time_of_day"] == "Morning"
    assert out.loc["CNR4", "time_of_day"] == "Night"
    assert out.loc["CNR2", "ride_outcome"] == "Cancelled"
    assert bool(out.loc["CNR1", "is_completed"]) is True


@skips_stub
def test_categories():
    df = m3.add_calculated_columns(m3.change_dtypes(prepared(2)))
    out = skip_if_stub(m3.add_categories, df).set_index("booking_id")
    assert out.loc["CNR1", "distance_category"] == "Short (<=10 km)"
    assert out.loc["CNR1", "fare_category"] == "Medium (250-500)"
    assert out.loc["CNR2", "fare_category"] == "Not Applicable"
    assert out.loc["CNR2", "fare_per_km"] == 0
    assert out.isna().sum().sum() == 0


@skips_stub
def test_outlier_flag():
    df = pd.DataFrame({"booking_value_inr": [300.0, 310.0, 320.0, 330.0, 340.0, 5000.0]})
    out = m3.flag_outliers(df)
    assert out["is_fare_outlier"].tolist() == [False] * 5 + [True]


@skips_stub
def test_sort_records():
    df = m3.add_categories(m3.add_calculated_columns(m3.change_dtypes(prepared(2))))
    srt = m3.sort_records(df.sample(frac=1, random_state=1))
    assert srt["booking_datetime"].is_monotonic_increasing
    assert list(srt.index) == list(range(len(srt)))

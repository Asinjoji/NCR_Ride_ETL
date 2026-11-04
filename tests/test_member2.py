import etl.member2_missing_and_validation as m2
from tests.conftest import skips_stub, prepared, skip_if_stub


@skips_stub
def test_reasons_merged_and_flags_dropped():
    df = skip_if_stub(m2.merge_reason_columns, prepared(1)).set_index("booking_id")
    assert df.loc["CNR2", "cancelled_by"] == "Driver"
    assert df.loc["CNR2", "reason"] == "Customer related issue"
    assert df.loc["CNR1", "reason"] == "Not Applicable"
    assert "cancelled_rides_by_driver" not in df.columns


@skips_stub
def test_missing_values_handled():
    merged = m2.merge_reason_columns(prepared(1))
    df = skip_if_stub(m2.handle_missing, m2.validate_and_filter(merged))
    row = df.set_index("booking_id").loc["CNR2"]
    assert row["payment_method"] == "Not Applicable"
    assert row["booking_value_inr"] == 0 and row["customer_rating"] == 0
    assert df.isna().sum().sum() == 0                     # no nulls anywhere


@skips_stub
def test_invalid_rating_removed():
    df = m2.merge_reason_columns(prepared(1))
    out = skip_if_stub(m2.validate_and_filter, df)
    assert "CNR3" not in set(out["booking_id"])           # driver rating 9.0
    assert "CNR1" in set(out["booking_id"])

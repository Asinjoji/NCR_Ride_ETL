import pandas as pd

import etl.member1_extract_structural as m1
from tests.conftest import skips_stub, make_sample, skip_if_stub


@skips_stub
def test_extract_reads_and_saves_raw_copy(tmp_path, monkeypatch):
    src = tmp_path / "in.csv"
    make_sample().to_csv(src, index=False)
    for name, value in [("RAW_DIR", tmp_path), ("BASE_DIR", tmp_path),
                        ("RAW_COPY", tmp_path / "copy.csv")]:
        monkeypatch.setattr(m1, name, value, raising=False)
    df = skip_if_stub(m1.extract, src)
    assert df.shape == (6, 21)
    assert (tmp_path / "copy.csv").exists()


@skips_stub
def test_rename_columns(sample):
    df = skip_if_stub(m1.rename_columns, sample)
    assert {"booking_id", "avg_vtat_min", "booking_value_inr", "driver_rating"} <= set(df.columns)
    assert " " not in "".join(df.columns)


@skips_stub
def test_text_standardised(sample):
    df = skip_if_stub(m1.standardise_text, m1.rename_columns(sample))
    assert not df["booking_id"].str.contains('"').any()
    assert "Palam Vihar" in set(df["pickup_location"])


@skips_stub
def test_duplicates_removed(sample):
    df = m1.standardise_text(m1.rename_columns(sample))
    out = skip_if_stub(m1.remove_duplicates, df)
    assert out["booking_id"].is_unique and len(out) == 5


@skips_stub
def test_dates_converted(sample):
    df = skip_if_stub(m1.convert_dates, m1.rename_columns(sample))
    assert pd.api.types.is_datetime64_any_dtype(df["booking_datetime"])
    assert "date" not in df.columns and "time" not in df.columns
    assert df["hour"].iloc[0] == 9 and df["day_of_week"].iloc[0] == "Tuesday"

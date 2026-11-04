import pytest

import etl.member4_reports_and_load as m4
import pipeline
from tests.conftest import skips_stub, make_sample, skip_if_stub

REQUIRED = ["booking_status_summary.csv", "vehicle_type_report.csv", "monthly_report.csv",
            "top10_pickup_locations.csv", "summary_statistics.csv"]


def clean():
    try:
        return pipeline.transform(make_sample(), upto_member=3)[0]
    except NotImplementedError:
        pytest.skip("members 1-3 are not merged yet")


@skips_stub
def test_at_least_three_reports():
    reports = skip_if_stub(m4.generate_reports, clean())
    assert len(reports) >= 3
    for name in REQUIRED:
        assert name in reports and len(reports[name]) > 0


@skips_stub
def test_report_values():
    reports = skip_if_stub(m4.generate_reports, clean())
    status = reports["booking_status_summary.csv"].set_index("booking_status")
    assert status.loc["Completed", "bookings"] == 3
    assert abs(status["share_pct"].sum() - 100) < 0.1
    vt = reports["vehicle_type_report.csv"].set_index("vehicle_type")
    assert vt.loc["Auto", "bookings"] == 2


@skips_stub
def test_load_writes_files(tmp_path, monkeypatch):
    df = clean()
    reports = skip_if_stub(m4.generate_reports, df)
    monkeypatch.setattr(m4, "OUTPUT_DIR", tmp_path / "output")
    monkeypatch.setattr(m4, "REPORTS_DIR", tmp_path / "reports")
    monkeypatch.setattr(m4, "BASE_DIR", tmp_path)
    paths = skip_if_stub(m4.load, df, reports)
    assert (tmp_path / "output" / "cleaned_ride_bookings.csv").exists()
    assert (tmp_path / "reports" / "monthly_report.csv").exists()
    assert len(paths) == len(reports) + 1

"""Shared paths, constants and helpers. Owned by the team lead: do not edit."""
from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "raw_data"
REPORTS_DIR = BASE_DIR / "reports"
OUTPUT_DIR = BASE_DIR / "output"
DEFAULT_SOURCE = RAW_DIR / "ncr_ride_bookings.csv"
RAW_COPY = RAW_DIR / "ncr_ride_bookings_raw_copy.csv"
CLEANED_FILE = "cleaned_ride_bookings.csv"
NA_LABEL = "Not Applicable"


def banner(text):
    print(f"\n{'=' * 64}\n{text}\n{'=' * 64}")


class StepLog:
    """Collects one line per transformation for reports/transformation_log.csv."""

    def __init__(self):
        self.rows = []

    def add(self, member, step, why, before, after, note=""):
        self.rows.append({"member": member, "step": step, "why": why, "rows_before": before,
                          "rows_after": after, "rows_changed": before - after, "note": note})
        print(f"[{len(self.rows):02d}] M{member} {step:<40} rows {before:>8,} -> {after:>8,}  {note}")

    def to_frame(self):
        return pd.DataFrame(self.rows)
